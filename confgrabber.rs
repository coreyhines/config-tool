use std::{
    fs::{self, File},
    io::{self, BufRead, BufReader, Write},
    path::Path,
    process::Command,
    time::{Duration, Instant},
};
use clap::{App, Arg};
use futures::future::join_all;
use reqwest::{
    header::{HeaderMap, HeaderValue, AUTHORIZATION},
    Client, StatusCode,
};
use tokio::task;
use url::Url;

// Constants
const PING_TIMEOUT_MS: u64 = 2000;
const MAX_RETRIES: u32 = 3;
const RETRY_BASE_DELAY_MS: u64 = 1000;

// Error type for our application
#[derive(Debug)]
enum ConfigError {
    IoError(io::Error),
    NetworkError(reqwest::Error),
    ParseError(String),
    DeviceUnavailable(String),
    AuthenticationError(String),
    UnknownError(String),
}

impl std::fmt::Display for ConfigError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ConfigError::IoError(e) => write!(f, "IO error: {}", e),
            ConfigError::NetworkError(e) => write!(f, "Network error: {}", e),
            ConfigError::ParseError(e) => write!(f, "Parse error: {}", e),
            ConfigError::DeviceUnavailable(e) => write!(f, "Device unavailable: {}", e),
            ConfigError::AuthenticationError(e) => write!(f, "Authentication error: {}", e),
            ConfigError::UnknownError(e) => write!(f, "Unknown error: {}", e),
        }
    }
}

impl std::error::Error for ConfigError {}

// Result type for our application
type ConfigResult<T> = Result<T, ConfigError>;

// Function to check if a device is available via ping
async fn check_device_availability(hostname: &str) -> ConfigResult<bool> {
    let output = Command::new("ping")
        .arg("-c")
        .arg("1")
        .arg("-W")
        .arg((PING_TIMEOUT_MS / 1000).to_string())
        .arg(hostname)
        .output()
        .map_err(ConfigError::IoError)?;

    Ok(output.status.success())
}

// Function to grab configuration from a single device
async fn grab_single_config(
    hostname: &str,
    user: &str,
    passwd: &str,
    directory: &str,
    sanitized: bool,
) -> ConfigResult<()> {
    let hostname = hostname.trim();
    
    // Check device availability
    if !check_device_availability(hostname).await? {
        return Err(ConfigError::DeviceUnavailable(format!(
            "{} does not respond to ping",
            hostname
        )));
    }

    // Create HTTP client with SSL verification disabled (similar to Python's _create_unverified_https_context)
    let mut headers = HeaderMap::new();
    let auth_value = format!("{}:{}", user, passwd);
    let auth_value = base64::encode(auth_value);
    headers.insert(
        AUTHORIZATION,
        HeaderValue::from_str(&format!("Basic {}", auth_value))
            .map_err(|e| ConfigError::ParseError(e.to_string()))?,
    );

    let client = Client::builder()
        .danger_accept_invalid_certs(true)
        .default_headers(headers)
        .build()
        .map_err(ConfigError::NetworkError)?;

    // Implement retry logic with exponential backoff
    let mut last_error = None;
    for attempt in 0..MAX_RETRIES {
        let cmd = if sanitized {
            "show running-config sanitized"
        } else {
            "show running-config"
        };

        let url = format!("https://{}/command-api", hostname);
        let url = Url::parse(&url).map_err(|e| ConfigError::ParseError(e.to_string()))?;

        let payload = serde_json::json!({
            "jsonrpc": "2.0",
            "method": "runCmds",
            "params": {
                "version": 1,
                "cmds": ["enable", cmd],
                "format": "text"
            },
            "id": "EapiExplorer-1"
        });

        match client.post(url).json(&payload).send().await {
            Ok(response) => {
                if response.status() == StatusCode::OK {
                    let result: serde_json::Value = response.json().await.map_err(ConfigError::NetworkError)?;
                    
                    if let Some(output) = result["result"][1]["output"].as_array() {
                        // Create directory if it doesn't exist
                        fs::create_dir_all(directory).map_err(ConfigError::IoError)?;
                        
                        // Write config to file
                        let output_path = Path::new(directory).join(format!("{}.txt", hostname));
                        let mut file = File::create(output_path).map_err(ConfigError::IoError)?;
                        
                        for line in output {
                            if let Some(line_str) = line.as_str() {
                                writeln!(file, "{}", line_str).map_err(ConfigError::IoError)?;
                            }
                        }
                        
                        println!("Successfully downloaded config from {}", hostname);
                        return Ok(());
                    } else {
                        last_error = Some(ConfigError::ParseError("Invalid response format".to_string()));
                    }
                } else if response.status() == StatusCode::UNAUTHORIZED {
                    return Err(ConfigError::AuthenticationError(format!(
                        "Authentication failed for {}",
                        hostname
                    )));
                } else {
                    last_error = Some(ConfigError::NetworkError(reqwest::Error::from(
                        io::Error::new(io::ErrorKind::Other, format!("HTTP error: {}", response.status())),
                    )));
                }
            }
            Err(e) => {
                last_error = Some(ConfigError::NetworkError(e));
            }
        }

        // Exponential backoff
        if attempt < MAX_RETRIES - 1 {
            let delay = RETRY_BASE_DELAY_MS * (1 << attempt);
            tokio::time::sleep(Duration::from_millis(delay)).await;
        }
    }

    Err(last_error.unwrap_or_else(|| {
        ConfigError::UnknownError(format!("Failed to grab config from {}", hostname))
    }))
}

// Function to grab configurations from multiple devices in parallel
async fn grab_configs(
    hostnames: Vec<String>,
    user: String,
    passwd: String,
    directory: String,
    sanitized: bool,
    max_workers: Option<usize>,
) -> ConfigResult<()> {
    // Create a semaphore to limit concurrent tasks if max_workers is specified
    let semaphore = if let Some(workers) = max_workers {
        Some(tokio::sync::Semaphore::new(workers))
    } else {
        None
    };

    // Create tasks for each hostname
    let mut tasks = Vec::new();
    for hostname in hostnames {
        let user_clone = user.clone();
        let passwd_clone = passwd.clone();
        let directory_clone = directory.clone();
        
        let task = task::spawn(async move {
            // If we have a semaphore, acquire a permit before processing
            let _permit = if let Some(sem) = &semaphore {
                Some(sem.acquire().await.unwrap())
            } else {
                None
            };
            
            match grab_single_config(&hostname, &user_clone, &passwd_clone, &directory_clone, sanitized).await {
                Ok(_) => (),
                Err(e) => eprintln!("Failed to download config from {}: {}", hostname, e),
            }
        });
        
        tasks.push(task);
    }

    // Wait for all tasks to complete
    join_all(tasks).await;
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let matches = App::new("Config Grabber")
        .version("1.0")
        .author("Your Name")
        .about("Downloads configurations from EOS devices")
        .arg(
            Arg::with_name("user")
                .short("u")
                .long("user")
                .value_name("USERNAME")
                .help("Specify a username")
                .required(true)
                .takes_value(true),
        )
        .arg(
            Arg::with_name("passwd")
                .short("p")
                .long("passwd")
                .value_name("PASSWORD")
                .help("For passing password interactively")
                .required(true)
                .takes_value(true),
        )
        .arg(
            Arg::with_name("file")
                .short("f")
                .long("file")
                .value_name("FILE")
                .help("Specify a file with EOS Devices from which to pull the running-config")
                .required(true)
                .takes_value(true),
        )
        .arg(
            Arg::with_name("directory")
                .short("d")
                .long("directory")
                .value_name("DIRECTORY")
                .help("Specify a directory to download configs to (note: no trailing '/')")
                .default_value(".")
                .takes_value(true),
        )
        .arg(
            Arg::with_name("sanitized")
                .short("s")
                .long("sanitized")
                .help("Flag for running-config to be sanitized: show running-config sanitized"),
        )
        .arg(
            Arg::with_name("workers")
                .short("w")
                .long("workers")
                .value_name("WORKERS")
                .help("Maximum number of worker threads (default: number of CPU cores)")
                .takes_value(true),
        )
        .get_matches();

    let user = matches.value_of("user").unwrap().to_string();
    let passwd = matches.value_of("passwd").unwrap().to_string();
    let file_path = matches.value_of("file").unwrap();
    let directory = matches.value_of("directory").unwrap().to_string();
    let sanitized = matches.is_present("sanitized");
    let max_workers = matches
        .value_of("workers")
        .and_then(|w| w.parse::<usize>().ok());

    // Read hostnames from file
    let file = File::open(file_path)?;
    let reader = BufReader::new(file);
    let hostnames: Vec<String> = reader.lines().filter_map(Result::ok).collect();

    // Start timing
    let start_time = Instant::now();

    // Grab configs in parallel
    grab_configs(
        hostnames.clone(),
        user,
        passwd,
        directory,
        sanitized,
        max_workers,
    )
    .await?;

    // Calculate and display execution time
    let execution_time = start_time.elapsed();
    println!(
        "\nProcessing {} EOS devices took {:.2} seconds",
        hostnames.len(),
        execution_time.as_secs_f64()
    );

    Ok(())
} 