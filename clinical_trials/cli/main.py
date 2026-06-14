"""Main CLI interface for clinical trials search"""

import sys
import argparse
import json
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rprint

from ..api.client import ClinicalTrialsClient, ClinicalTrialsAPIError
from ..models.search import SearchParams, SearchResult
from ..models.study import StudyStatus, StudyPhase
from ..utils.formatters import StudyFormatter


console = Console()


class ClinicalTrialsCLI:
    """Command-line interface for clinical trials search"""
    
    def __init__(self):
        self.client = ClinicalTrialsClient()
        self.formatter = StudyFormatter()
    
    def search_command(self, args: argparse.Namespace) -> None:
        """Execute search command"""
        try:
            # Build search parameters
            search_params = SearchParams(
                condition=args.condition,
                intervention=args.intervention,
                sponsor=args.sponsor,
                country=args.country,
                city=args.city,
                recruiting_only=args.recruiting,
                max_studies=args.max_studies
            )
            
            # Parse status filter
            if args.status:
                try:
                    search_params.status = StudyStatus(args.status)
                except ValueError:
                    console.print(f"[red]Invalid status: {args.status}[/red]")
                    return
            
            # Parse phase filter
            if args.phase:
                try:
                    search_params.phase = StudyPhase(args.phase)
                except ValueError:
                    console.print(f"[red]Invalid phase: {args.phase}[/red]")
                    return
            
            # Perform search with progress bar
            with Progress() as progress:
                task = progress.add_task("Searching clinical trials...", total=1)
                result = self.client.search(search_params)
                progress.update(task, completed=1)
            
            # Display results
            self._display_search_results(result, args)
            
        except ClinicalTrialsAPIError as e:
            console.print(f"[red]API Error: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    def study_command(self, args: argparse.Namespace) -> None:
        """Execute study details command"""
        try:
            study = self.client.get_study(args.nct_id)
            if study:
                self.formatter.display_study_details(study, console)
            else:
                console.print(f"[red]Study not found: {args.nct_id}[/red]")
                
        except ClinicalTrialsAPIError as e:
            console.print(f"[red]API Error: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    def info_command(self, args: argparse.Namespace) -> None:
        """Execute API info command"""
        try:
            info = self.client.get_api_info()
            console.print(Panel(json.dumps(info, indent=2), title="API Information"))
            
        except ClinicalTrialsAPIError as e:
            console.print(f"[red]API Error: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    def _display_search_results(self, result: SearchResult, args: argparse.Namespace) -> None:
        """Display search results"""
        if not result.studies:
            console.print("[yellow]No studies found matching your criteria.[/yellow]")
            return
        
        console.print(f"\n[green]Found {result.total_count} clinical trials[/green]")
        
        # Display format options
        if args.format == "table":
            self.formatter.display_studies_table(result.studies, console)
        elif args.format == "summary":
            self.formatter.display_studies_summary(result.studies, console)
        elif args.format == "json":
            self._export_json(result.studies, args.output)
        elif args.format == "csv":
            self._export_csv(result.studies, args.output)
        else:
            self.formatter.display_studies_list(result.studies, console)
        
        # Display statistics
        if args.stats:
            self._display_statistics(result)
    
    def _display_statistics(self, result: SearchResult) -> None:
        """Display search result statistics"""
        console.print("\n[bold]Statistics:[/bold]")
        
        # Status distribution
        status_groups = result.group_by_status()
        if status_groups:
            status_table = Table(title="Status Distribution")
            status_table.add_column("Status", style="cyan")
            status_table.add_column("Count", style="green")
            
            for status, studies in status_groups.items():
                status_table.add_row(status.value, str(len(studies)))
            
            console.print(status_table)
        
        # Phase distribution
        phase_groups = result.group_by_phase()
        if phase_groups:
            phase_table = Table(title="Phase Distribution")
            phase_table.add_column("Phase", style="cyan")
            phase_table.add_column("Count", style="green")
            
            for phase, studies in phase_groups.items():
                phase_table.add_row(phase.value, str(len(studies)))
            
            console.print(phase_table)
    
    def _export_json(self, studies: List, output: Optional[str]) -> None:
        """Export studies to JSON"""
        data = [study.raw_data for study in studies]
        
        if output:
            with open(output, 'w') as f:
                json.dump(data, f, indent=2)
            console.print(f"[green]Results exported to {output}[/green]")
        else:
            console.print(json.dumps(data, indent=2))
    
    def _export_csv(self, studies: List, output: Optional[str]) -> None:
        """Export studies to CSV"""
        import csv
        import io
        
        if not studies:
            return
        
        # Determine CSV fields
        fields = ["nct_id", "brief_title", "overall_status", "phase", "conditions"]
        
        output_buffer = io.StringIO()
        writer = csv.writer(output_buffer)
        writer.writerow(fields)
        
        for study in studies:
            row = [
                study.nct_id,
                study.brief_title,
                study.overall_status.value if study.overall_status else "",
                study.phase.value if study.phase else "",
                "; ".join(study.conditions)
            ]
            writer.writerow(row)
        
        csv_content = output_buffer.getvalue()
        
        if output:
            with open(output, 'w') as f:
                f.write(csv_content)
            console.print(f"[green]Results exported to {output}[/green]")
        else:
            console.print(csv_content)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Search and retrieve clinical trial data from ClinicalTrials.gov"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for clinical trials")
    search_parser.add_argument("--condition", "-c", help="Medical condition")
    search_parser.add_argument("--intervention", "-i", help="Intervention/treatment")
    search_parser.add_argument("--sponsor", "-s", help="Study sponsor")
    search_parser.add_argument("--status", help="Study status")
    search_parser.add_argument("--phase", help="Study phase")
    search_parser.add_argument("--country", help="Country")
    search_parser.add_argument("--city", help="City")
    search_parser.add_argument("--recruiting", action="store_true", help="Recruiting studies only")
    search_parser.add_argument("--max-studies", type=int, default=10, help="Maximum studies to return")
    search_parser.add_argument("--format", choices=["list", "table", "summary", "json", "csv"], 
                              default="list", help="Output format")
    search_parser.add_argument("--output", "-o", help="Output file path")
    search_parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    # Study details command
    study_parser = subparsers.add_parser("study", help="Get study details")
    study_parser.add_argument("nct_id", help="NCT ID of the study")
    
    # API info command
    info_parser = subparsers.add_parser("info", help="Get API information")
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = ClinicalTrialsCLI()
    
    if args.command == "search":
        cli.search_command(args)
    elif args.command == "study":
        cli.study_command(args)
    elif args.command == "info":
        cli.info_command(args)


if __name__ == "__main__":
    main()