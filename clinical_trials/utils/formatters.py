"""Formatters for displaying clinical trial data"""

from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..models.study import Study


class StudyFormatter:
    """Formatter for displaying study information"""
    
    def display_studies_list(self, studies: List[Study], console: Console) -> None:
        """Display studies as a simple list"""
        for i, study in enumerate(studies, 1):
            status_color = self._get_status_color(study)
            
            console.print(f"\n[bold cyan]{i}. {study.nct_id}[/bold cyan]")
            console.print(f"   [bold]{study.brief_title}[/bold]")
            
            if study.overall_status:
                console.print(f"   Status: [{status_color}]{study.overall_status.value}[/{status_color}]")
            
            if study.phase:
                console.print(f"   Phase: [yellow]{study.phase.value}[/yellow]")
            
            if study.conditions:
                console.print(f"   Conditions: [magenta]{', '.join(study.conditions)}[/magenta]")
            
            if study.primary_location:
                location = study.primary_location
                console.print(f"   Location: [blue]{location.full_address}[/blue]")
            
            if study.url:
                console.print(f"   URL: [link]{study.url}[/link]")
    
    def display_studies_table(self, studies: List[Study], console: Console) -> None:
        """Display studies in a table format"""
        table = Table(title="Clinical Trials Search Results")
        table.add_column("NCT ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="bold")
        table.add_column("Status", style="green")
        table.add_column("Phase", style="yellow")
        table.add_column("Conditions", style="magenta")
        table.add_column("Location", style="blue")
        
        for study in studies:
            title = study.brief_title[:60] + "..." if len(study.brief_title) > 60 else study.brief_title
            status = study.overall_status.value if study.overall_status else "Unknown"
            phase = study.phase.value if study.phase else "N/A"
            conditions = ", ".join(study.conditions[:2])  # Show first 2 conditions
            if len(study.conditions) > 2:
                conditions += "..."
            
            location = "N/A"
            if study.primary_location:
                loc = study.primary_location
                if loc.city and loc.country:
                    location = f"{loc.city}, {loc.country}"
                elif loc.country:
                    location = loc.country
            
            table.add_row(study.nct_id, title, status, phase, conditions, location)
        
        console.print(table)
    
    def display_studies_summary(self, studies: List[Study], console: Console) -> None:
        """Display a summary of studies"""
        for study in studies:
            panel_content = []
            
            if study.overall_status:
                status_color = self._get_status_color(study)
                panel_content.append(f"Status: [{status_color}]{study.overall_status.value}[/{status_color}]")
            
            if study.phase:
                panel_content.append(f"Phase: [yellow]{study.phase.value}[/yellow]")
            
            if study.conditions:
                panel_content.append(f"Conditions: [magenta]{', '.join(study.conditions)}[/magenta]")
            
            if study.brief_summary:
                summary = study.brief_summary[:200] + "..." if len(study.brief_summary) > 200 else study.brief_summary
                panel_content.append(f"\n[dim]{summary}[/dim]")
            
            panel_text = "\n".join(panel_content)
            console.print(Panel(panel_text, title=f"[bold cyan]{study.nct_id}[/bold cyan]: {study.brief_title}"))
    
    def display_study_details(self, study: Study, console: Console) -> None:
        """Display detailed information for a single study"""
        # Title panel
        console.print(Panel(
            f"[bold]{study.brief_title}[/bold]\n"
            f"[dim]{study.official_title or 'No official title'}[/dim]",
            title=f"[bold cyan]{study.nct_id}[/bold cyan]"
        ))
        
        # Basic info table
        info_table = Table(title="Study Information", show_header=False)
        info_table.add_column("Field", style="bold cyan")
        info_table.add_column("Value")
        
        if study.overall_status:
            status_color = self._get_status_color(study)
            info_table.add_row("Status", f"[{status_color}]{study.overall_status.value}[/{status_color}]")
        
        if study.phase:
            info_table.add_row("Phase", f"[yellow]{study.phase.value}[/yellow]")
        
        if study.study_type:
            info_table.add_row("Study Type", study.study_type)
        
        if study.primary_purpose:
            info_table.add_row("Primary Purpose", study.primary_purpose)
        
        if study.enrollment:
            info_table.add_row("Enrollment", str(study.enrollment))
        
        console.print(info_table)
        
        # Conditions
        if study.conditions:
            console.print(Panel(
                ", ".join(study.conditions),
                title="[bold magenta]Conditions[/bold magenta]"
            ))
        
        # Interventions
        if study.interventions:
            console.print(Panel(
                ", ".join(study.interventions),
                title="[bold green]Interventions[/bold green]"
            ))
        
        # Locations
        if study.locations:
            locations_text = []
            for loc in study.locations[:5]:  # Show first 5 locations
                locations_text.append(loc.full_address)
            
            if len(study.locations) > 5:
                locations_text.append(f"... and {len(study.locations) - 5} more locations")
            
            console.print(Panel(
                "\n".join(locations_text),
                title="[bold blue]Locations[/bold blue]"
            ))
        
        # Sponsors
        if study.sponsors:
            sponsors_text = []
            for sponsor in study.sponsors:
                sponsor_info = sponsor.name
                if sponsor.agency_class:
                    sponsor_info += f" ({sponsor.agency_class})"
                sponsors_text.append(sponsor_info)
            
            console.print(Panel(
                "\n".join(sponsors_text),
                title="[bold orange]Sponsors[/bold orange]"
            ))
        
        # Summary
        if study.brief_summary:
            console.print(Panel(
                study.brief_summary,
                title="[bold]Brief Summary[/bold]"
            ))
        
        # Detailed description (truncated)
        if study.detailed_description:
            description = study.detailed_description[:500] + "..." if len(study.detailed_description) > 500 else study.detailed_description
            console.print(Panel(
                description,
                title="[bold]Detailed Description[/bold]"
            ))
        
        # URL
        if study.url:
            console.print(f"\n[link]{study.url}[/link]")
    
    def _get_status_color(self, study: Study) -> str:
        """Get color for study status"""
        if not study.overall_status:
            return "dim"
        
        status_colors = {
            "Recruiting": "green",
            "Not yet recruiting": "yellow",
            "Active, not recruiting": "blue",
            "Completed": "dim",
            "Terminated": "red",
            "Suspended": "orange",
            "Withdrawn": "red"
        }
        
        return status_colors.get(study.overall_status.value, "white")