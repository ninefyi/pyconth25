#!/usr/bin/env python3
"""
MongoDB Atlas Projects Viewer using Textual Framework
Python 3.12+ compatible

This application uses the MongoDB Atlas Administration API to list all projects
in your Atlas organization using a modern terminal UI built with Textual.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import (
    Header, Footer, Static, DataTable
)
from textual.reactive import reactive
from textual.screen import Screen
from textual import on

# Load environment variables
load_dotenv()

class ProjectData:
    """Data model for Atlas projects."""
    
    def __init__(self, project_data: Dict[str, Any]):
        self.id = project_data.get('id', '')
        self.name = project_data.get('name', '')
        self.org_id = project_data.get('orgId', '')
        self.created = project_data.get('created', '')
        self.cluster_count = project_data.get('clusterCount', 0)
        self.links = project_data.get('links', [])


class ClusterData:
    """Data model for Atlas clusters."""
    
    def __init__(self, cluster_data: Dict[str, Any]):
        self.id = cluster_data.get('id', '')
        self.name = cluster_data.get('name', '')
        self.connection_strings = cluster_data.get('connectionStrings', {})
        self.cluster_type = cluster_data.get('clusterType', '')
        self.mongo_db_version = cluster_data.get('mongoDBVersion', '')
        self.state_name = cluster_data.get('stateName', '')
        self.created_date = cluster_data.get('createDate', '')
        self.provider_settings = cluster_data.get('providerSettings', {})
        self.backup_enabled = cluster_data.get('backupEnabled', False)
        self.encryption_at_rest_provider = cluster_data.get('encryptionAtRestProvider', '')
        
        # Extract provider and region info
        if self.provider_settings:
            self.provider_name = self.provider_settings.get('providerName', 'Unknown')
            self.region_name = self.provider_settings.get('regionName', 'Unknown')
            self.instance_size_name = self.provider_settings.get('instanceSizeName', 'Unknown')
        else:
            self.provider_name = 'Unknown'
            self.region_name = 'Unknown'
            self.instance_size_name = 'Unknown'


class AtlasAPI:
    """MongoDB Atlas Administration API client."""
    
    def __init__(self, public_key: str, private_key: str):
        self.public_key = public_key
        self.private_key = private_key
        self.base_url = "https://cloud.mongodb.com/api/atlas/v2"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def delete_one_project(self, project_id: str) -> bool:
        """Delete a project from Atlas API."""
        url = f"{self.base_url}/groups/{project_id}"
        
        try:
            # Use HTTP Digest Authentication with API keys
            auth = httpx.DigestAuth(self.public_key, self.private_key)
            headers = {
                "Accept": "application/vnd.atlas.2023-01-01+json",
                "Content-Type": "application/json"
            }
            
            response = await self.client.delete(url, auth=auth, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise Exception(f"API request failed: {e}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API")
        
        return True
    
    async def get_projects(self) -> List[ProjectData]:
        """Fetch all projects from Atlas API."""
        url = f"{self.base_url}/groups"
        
        try:
            # Use HTTP Digest Authentication with API keys
            auth = httpx.DigestAuth(self.public_key, self.private_key)
            headers = {
                "Accept": "application/vnd.atlas.2023-01-01+json",
                "Content-Type": "application/json"
            }
            
            response = await self.client.get(url, auth=auth, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            projects = []
            
            for project_data in data.get('results', []):
                projects.append(ProjectData(project_data))
            
            return projects
            
        except httpx.HTTPError as e:
            raise Exception(f"API request failed: {e}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API")
    
    async def get_clusters(self, project_id: str) -> List[ClusterData]:
        """Fetch all clusters for a specific project from Atlas API."""
        url = f"{self.base_url}/groups/{project_id}/clusters"
        
        try:
            # Use HTTP Digest Authentication with API keys
            auth = httpx.DigestAuth(self.public_key, self.private_key)
            headers = {
                "Accept": "application/vnd.atlas.2023-01-01+json",
                "Content-Type": "application/json"
            }
            
            response = await self.client.get(url, auth=auth, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            clusters = []
            
            for cluster_data in data.get('results', []):
                clusters.append(ClusterData(cluster_data))
            
            return clusters
            
        except httpx.HTTPError as e:
            raise Exception(f"API request failed: {e}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class ProjectsTable(DataTable):
    """Custom DataTable for displaying Atlas projects."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        
    def on_mount(self) -> None:
        """Set up the table columns."""
        self.add_columns("Project Name", "Project ID", "Created Date")


class ClustersTable(DataTable):
    """Custom DataTable for displaying Atlas clusters."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        
    def on_mount(self) -> None:
        """Set up the table columns."""
        self.add_columns("Cluster Name", "Status", "Provider", "Region", "Instance Size", "MongoDB Version")


class ClusterViewScreen(Screen):
    """Screen for viewing clusters in a specific project."""
    
    BINDINGS = [
        ("escape", "back", ""),
        ("q", "quit", ""),
    ]
    
    def __init__(self, project_data: ProjectData, api_client: AtlasAPI):
        super().__init__()
        self.project_data = project_data
        self.api_client = api_client
        self.clusters: List[ClusterData] = []
    
    def compose(self) -> ComposeResult:
        """Compose the cluster view UI."""
        yield Header(show_clock=True)
        with Container(classes="container"):
            # Header section
            with Vertical(classes="header-section"):
                yield Static(f"Clusters in Project: {self.project_data.name}", classes="title")
                yield Static(f"Project ID: {self.project_data.id}", classes="subtitle")
            
            # Table section
            with Vertical(classes="table-section"):
                yield ClustersTable(id="clusters_table")
            
            # Status section
            with Vertical(classes="status-section"):
                yield Static("Loading clusters...", id="cluster_status_display", classes="status")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the cluster view."""
        self.title = f"Clusters - {self.project_data.name}"
        await self.fetch_clusters()
    
    async def fetch_clusters(self) -> None:
        """Fetch clusters for the current project."""
        try:
            await self.update_status("Loading clusters...")
            
            # Fetch clusters
            clusters = await self.api_client.get_clusters(self.project_data.id)
            self.clusters = clusters
            
            # Update the table
            await self.update_clusters_table()
            
            count = len(clusters)
            await self.update_status(f"Successfully loaded {count} cluster{'s' if count != 1 else ''}")
            
        except Exception as e:
            await self.update_status(f"Error loading clusters: {str(e)}")
    
    async def update_clusters_table(self) -> None:
        """Update the clusters table with fetched data."""
        table = self.query_one("#clusters_table", ClustersTable)
        table.clear()
        
        for cluster in self.clusters:
            table.add_row(
                cluster.name or "Unnamed Cluster",
                cluster.state_name or "Unknown",
                cluster.provider_name,
                cluster.region_name,
                cluster.instance_size_name,
                cluster.mongo_db_version or "Unknown"
            )
    
    async def update_status(self, message: str) -> None:
        """Update the status display."""
        status_display = self.query_one("#cluster_status_display", Static)
        status_display.update(message)
    
    def action_back(self) -> None:
        """Go back to the projects view."""
        self.app.pop_screen()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class AtlasProjectsApp(App):
    """Main Textual application for managing Atlas projects."""

    CSS_PATH = "atlas_projects_manager.tcss"

    BINDINGS = [
        ("a", "authenticate", ""),
        ("n", "create", ""),
        ("d", "delete", ""),
        ("v", "cluster", ""),
        ("q", "quit", ""),
    ]
    
    # Reactive attributes
    status_message = reactive("")
    projects: List[ProjectData] = []
    public_key: str = ""
    private_key: str = ""
    org_id: str = ""
    
    def __init__(self):
        super().__init__()
        self.api_client: Optional[AtlasAPI] = None
        self.public_key = os.getenv('ATLAS_PUBLIC_KEY', '')
        self.private_key = os.getenv('ATLAS_PRIVATE_KEY', '')
        self.org_id = os.getenv('ATLAS_ORG_ID', '')
        
    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield Header(show_clock=True)
        with Container(classes="container"):
            # Header section
            with Vertical(classes="header-section"):
                yield Static("MongoDB Atlas Projects Manager", classes="title")
            # Table section
            with Vertical(classes="table-section"):
                yield ProjectsTable(id="projects_table")
            
            # Status section
            with Vertical(classes="status-section"):
                yield Static("Ready", id="status_display", classes="status")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application."""
        self.title = "MongoDB Atlas Projects Manager"
        

        if not all([
            os.getenv('ATLAS_PUBLIC_KEY'),
            os.getenv('ATLAS_PRIVATE_KEY'),
            os.getenv('ATLAS_ORG_ID')
        ]):
            self.update_status("Missing environment variables. Check .env file")
        else:
            self.update_status(f"Credentials loaded from environment variables", "success")


    async def fetch_projects(self, public_key: str, private_key: str) -> None:
        """Fetch projects from Atlas API."""
        await self.update_status("Loading projects...", "")
        try:
            # Close existing client if any
            if self.api_client:
                await self.api_client.close()
            
            # Create new API client
            self.api_client = AtlasAPI(public_key, private_key)
            
            # Fetch projects
            projects = await self.api_client.get_projects()
            self.projects = projects
            
            # Update the table
            await self.update_projects_table()
            
            count = len(projects)
            await self.update_status(f"Successfully loaded {count} project{'s' if count != 1 else ''}", "success")
            
        except Exception as e:
            await self.update_status(f"Error: {str(e)}", "error")
    
    async def update_projects_table(self) -> None:
        """Update the projects table with fetched data."""
        table = self.query_one("#projects_table", ProjectsTable)
        table.clear()
        
        for project in self.projects:
            # Format the created date
            created_date = "N/A"
            if project.created:
                try:
                    dt = datetime.fromisoformat(project.created.replace('Z', '+00:00'))
                    created_date = dt.strftime('%d-%b-%Y %H:%M')
                except:
                    created_date = project.created[:19]  # Take first 19 chars
            
            table.add_row(
                project.name or "Unnamed Project",
                project.id,
                created_date
            )
    
    async def update_status(self, message: str, status_type: str = "") -> None:
        """Update the status display."""
        status_display = self.query_one("#status_display", Static)
        status_display.update(message)
        
        # Update CSS classes based on status type
        status_display.remove_class("error", "success")
        if status_type:
            status_display.add_class(status_type)
    
    async def on_exit(self) -> None:
        """Clean up when exiting."""
        if self.api_client:
            await self.api_client.close()


    async def action_quit(self):
        self.exit()
    
    async def action_delete(self):
        table = self.query_one("#projects_table", DataTable)

        if table.cursor_row is None or table.cursor_row < 0:
            await self.update_status("Please select a project to delete")
            return

        try:
            # row_key = table.coordinate_to_cell_key(table.cursor_row)       
            await self.update_status(f"Deleting project...{table.cursor_row}")     
            selected_row = table.get_row_at(table.cursor_row)
            project_name = selected_row[0]
            project_id = selected_row[1]

            await self.update_status(f"Deleting project: {project_name} - {project_id}")

            self.api_client = AtlasAPI(self.public_key, self.private_key)
            await self.api_client.delete_one_project(project_id)
            await self.update_status(f"Project deleted: {project_name} - {project_id}", "success")
            await self.fetch_projects(self.public_key, self.private_key)

        except (IndexError, StopIteration):
            await self.update_status("Could not find selected project", "error")


    async def action_authenticate(self):
        """Authenticate with Azure"""
        await self.update_status("Authenticating...")
        await self.fetch_projects(self.public_key, self.private_key)

    async def action_cluster(self):
        """View clusters for the selected project."""
        table = self.query_one("#projects_table", DataTable)

        if table.cursor_row is None or table.cursor_row < 0:
            await self.update_status("Please select a project to view clusters")
            return

        try:
            selected_row = table.get_row_at(table.cursor_row)
            project_name = selected_row[0]
            project_id = selected_row[1]

            # Find the project data
            selected_project = None
            for project in self.projects:
                if project.id == project_id:
                    selected_project = project
                    break

            if selected_project:
                await self.update_status(f"Opening clusters for: {project_name}")
                
                # Create API client if not available
                if not self.api_client:
                    self.api_client = AtlasAPI(self.public_key, self.private_key)
                
                # Push the cluster view screen
                cluster_screen = ClusterViewScreen(selected_project, self.api_client)
                self.push_screen(cluster_screen)
            else:
                await self.update_status("Could not find project data", "error")

        except (IndexError, Exception) as e:
            await self.update_status(f"Error viewing clusters: {str(e)}", "error")

    @on(DataTable.RowSelected)
    async def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the projects table."""
        if event.data_table.id == "projects_table":
            # Auto-open clusters when a project row is selected
            await self.action_cluster()
            self.refresh_bindings()


def main():
    """Main entry point."""
    app = AtlasProjectsApp()
    app.run()


if __name__ == "__main__":
    main()