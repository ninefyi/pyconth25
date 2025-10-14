# PyConTH25 - MongoDB Atlas Projects Viewer

<h2>Boosting Operational Productivity with Python and Textual: Modern Terminal Dashboards for Developers</h2>

A modern terminal-based application built with Python 3.12+ and the Textual framework to view and manage MongoDB Atlas projects.

## Features

- 🎯 **Modern TUI**: Beautiful terminal user interface powered by Textual
- 🔐 **Secure Authentication**: Uses MongoDB Atlas Administration API v2.0
- 📊 **Project Overview**: View all your Atlas projects in a clean table format
- 🌍 **Environment Support**: Load credentials from environment variables
- ⚡ **Async Performance**: Fast, non-blocking HTTP requests with httpx

## Prerequisites

- Python 3.8 or higher (recommended: Python 3.12+)
- MongoDB Atlas account with API access
- Atlas API Key (Public + Private Key pair)

## Quick Start

1. **Clone and setup**:
   ```bash
   cd pyconth25
   python setup.py
   ```

2. **Configure your Atlas API credentials**:
   ```bash
   # Edit the .env file with your credentials
   nano .env
   ```

   Add your Atlas API credentials:
   ```env
   ATLAS_PUBLIC_KEY=your_public_key_here
   ATLAS_PRIVATE_KEY=your_private_key_here
   ```

3. **Run the application**:
   ```bash
   python atlas_projects_viewer.py
   ```

## Getting Atlas API Credentials

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com)
2. Go to **Access Manager** → **API Keys**
3. Click **Create API Key**
4. Add a description and select appropriate permissions:
   - **Organization Member** (minimum)
   - **Project Read Only** or higher for project access
5. Copy the **Public Key** and **Private Key**
6. Add your current IP to the API Access List

## Application Features

### Main Interface
- **Credentials Input**: Enter your Atlas API keys
- **Projects Table**: View all projects with:
  - Project Name
  - Project ID
  - Organization ID
  - Creation Date
- **Status Display**: Real-time feedback on operations

### Keyboard Shortcuts
- `Ctrl+C` or `q`: Quit the application
- `Tab`: Navigate between input fields
- `Enter`: Load projects (when button is focused)

## Architecture

The application is built with:

- **Textual Framework**: Modern TUI framework for Python
- **httpx**: Modern async HTTP client
- **MongoDB Atlas API v2.0**: Official REST API for Atlas management
- **Python 3.12+**: Latest Python features and performance

### File Structure
```
pyconth25/
├── atlas_projects_viewer.py    # Main application
├── requirements.txt             # Python dependencies
├── setup.py                    # Setup script
├── .env.example               # Environment template
├── .env                       # Your credentials (create this)
└── README.md                  # This file
```

## API Integration

This application uses the MongoDB Atlas Administration API v2.0:

- **Base URL**: `https://cloud.mongodb.com/api/atlas/v2`
- **Authentication**: HTTP Digest Authentication
- **Endpoint**: `/groups` (lists all projects)
- **API Version**: `application/vnd.atlas.2023-01-01+json`

## Development

### Requirements
All dependencies are listed in `requirements.txt`:
- `httpx`: Async HTTP client
- `textual[dev]`: TUI framework with development tools
- `rich`: Terminal formatting
- `python-dotenv`: Environment variable management

### Running in Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with development features
python atlas_projects_viewer.py
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Authentication errors**: Verify your API credentials
   - Check Public Key and Private Key are correct
   - Ensure your IP is in the API Access List
   - Verify API key has necessary permissions

3. **Connection errors**: Check your internet connection and Atlas status

### Error Messages
- `API request failed`: Check credentials and network connection
- `Invalid JSON response`: Atlas API may be unavailable
- `Please enter both keys`: Both Public and Private keys are required

## Contributing

This is a PyCon Thailand 2025 demonstration project showcasing modern Python development with Textual framework.

## License

MIT License - feel free to use and modify for your projects.

## MongoDB Atlas Resources

- [Atlas Administration API Documentation](https://www.mongodb.com/docs/atlas/api/atlas-admin-api/)
- [API Authentication Guide](https://www.mongodb.com/docs/atlas/configure-api-access/)
- [Atlas API Reference](https://www.mongodb.com/docs/atlas/api/atlas-admin-api-ref/)
- [Postman Collection](https://www.postman.com/mongodb-devrel/workspace/mongodb-atlas-administration-apis/)

## Legacy Instructions
1. copy .env.template to .env
2. run `python atlas_projects_manager.py`
