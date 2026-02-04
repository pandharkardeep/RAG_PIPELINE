import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChartService, ChartOutput, ExtractedData, ChartType } from '../../core/services/chart.service';

@Component({
    selector: 'app-chart-extractor',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './chart-extractor.html',
    styleUrl: './chart-extractor.scss'
})
export class ChartExtractor implements OnInit {
    // Input state
    inputText: string = '';
    inputUrl: string = '';

    // Extracted data state
    extractedData: ExtractedData | null = null;
    dataPreview: any[] = [];

    // Generated charts
    generatedCharts: ChartOutput[] = [];

    // Available chart types
    chartTypes: ChartType[] = [];
    selectedChartTypes: string[] = [];

    // UI state
    isLoading: boolean = false;
    isExtracting: boolean = false;
    isGenerating: boolean = false;
    hasExtractedData: boolean = false;
    hasCharts: boolean = false;
    errorMessage: string = '';
    successMessage: string = '';
    activeTab: 'input' | 'preview' | 'charts' = 'input';

    constructor(private chartService: ChartService) { }

    ngOnInit(): void {
        this.loadChartTypes();
    }

    loadChartTypes(): void {
        this.chartService.getChartTypes().subscribe({
            next: (response) => {
                this.chartTypes = response.chart_types;
            },
            error: (err) => {
                console.error('Failed to load chart types:', err);
            }
        });
    }

    extractData(): void {
        if (!this.inputText.trim() && !this.inputUrl.trim()) {
            this.errorMessage = 'Please provide article text or a URL';
            return;
        }

        this.isExtracting = true;
        this.errorMessage = '';
        this.successMessage = '';

        this.chartService.extractData(
            this.inputText.trim() || undefined,
            this.inputUrl.trim() || undefined
        ).subscribe({
            next: (response) => {
                this.isExtracting = false;
                if (response.success) {
                    this.extractedData = response.extracted_data;
                    this.dataPreview = response.data_preview;
                    this.hasExtractedData = true;
                    this.successMessage = response.message;
                    this.activeTab = 'preview';
                } else {
                    this.errorMessage = response.message || 'No data could be extracted';
                }
            },
            error: (err) => {
                this.isExtracting = false;
                this.errorMessage = err.error?.detail || 'Failed to extract data';
                console.error('Extraction error:', err);
            }
        });
    }

    generateCharts(): void {
        if (!this.extractedData) {
            this.errorMessage = 'Please extract data first';
            return;
        }

        this.isGenerating = true;
        this.errorMessage = '';
        this.successMessage = '';

        const chartTypesToGenerate = this.selectedChartTypes.length > 0
            ? this.selectedChartTypes
            : undefined;

        this.chartService.generateCharts(this.extractedData, chartTypesToGenerate).subscribe({
            next: (response) => {
                this.isGenerating = false;
                if (response.success) {
                    this.generatedCharts = response.charts;
                    this.hasCharts = true;
                    this.successMessage = response.message;
                    this.activeTab = 'charts';
                } else {
                    this.errorMessage = response.message || 'No charts could be generated';
                }
            },
            error: (err) => {
                this.isGenerating = false;
                this.errorMessage = err.error?.detail || 'Failed to generate charts';
                console.error('Chart generation error:', err);
            }
        });
    }

    runFullPipeline(): void {
        if (!this.inputText.trim() && !this.inputUrl.trim()) {
            this.errorMessage = 'Please provide article text or a URL';
            return;
        }

        this.isLoading = true;
        this.errorMessage = '';
        this.successMessage = '';

        this.chartService.fullPipeline(
            this.inputText.trim() || undefined,
            this.inputUrl.trim() || undefined
        ).subscribe({
            next: (response) => {
                this.isLoading = false;
                if (response.success) {
                    this.extractedData = response.extracted_data;
                    this.generatedCharts = response.charts;
                    this.hasExtractedData = true;
                    this.hasCharts = response.charts.length > 0;
                    this.successMessage = response.message;
                    this.activeTab = 'charts';
                } else {
                    this.errorMessage = response.message || 'Pipeline failed';
                }
            },
            error: (err) => {
                this.isLoading = false;
                this.errorMessage = err.error?.detail || 'Pipeline failed';
                console.error('Pipeline error:', err);
            }
        });
    }

    downloadChart(chart: ChartOutput, index: number): void {
        const filename = `chart_${index + 1}_${chart.chart_type}.png`;
        this.chartService.downloadChart(chart.png_base64, filename);
    }

    downloadAllCharts(): void {
        this.chartService.downloadAllAsZip(this.generatedCharts);
    }

    copyCaption(caption: string): void {
        navigator.clipboard.writeText(caption);
        this.successMessage = 'Caption copied to clipboard!';
        setTimeout(() => this.successMessage = '', 2000);
    }

    copyAllCaptions(): void {
        const allCaptions = this.generatedCharts.map((c, i) => `[Chart ${i + 1}] ${c.caption}`).join('\n\n');
        navigator.clipboard.writeText(allCaptions);
        this.successMessage = 'All captions copied to clipboard!';
        setTimeout(() => this.successMessage = '', 2000);
    }

    clearAll(): void {
        this.inputText = '';
        this.inputUrl = '';
        this.extractedData = null;
        this.dataPreview = [];
        this.generatedCharts = [];
        this.hasExtractedData = false;
        this.hasCharts = false;
        this.errorMessage = '';
        this.successMessage = '';
        this.selectedChartTypes = [];
        this.activeTab = 'input';
    }

    toggleChartType(typeId: string): void {
        const index = this.selectedChartTypes.indexOf(typeId);
        if (index > -1) {
            this.selectedChartTypes.splice(index, 1);
        } else {
            this.selectedChartTypes.push(typeId);
        }
    }

    isChartTypeSelected(typeId: string): boolean {
        return this.selectedChartTypes.includes(typeId);
    }

    get totalChars(): number {
        return this.inputText.length;
    }

    getChartImageUrl(base64: string): string {
        return `data:image/png;base64,${base64}`;
    }
}
