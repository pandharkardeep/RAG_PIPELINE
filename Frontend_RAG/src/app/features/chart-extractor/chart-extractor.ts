import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgxEchartsModule } from 'ngx-echarts';
import { ChartService, ChartOutput, ExtractedData, ChartType } from '../../core/services/chart.service';
import { GlobalHeader } from '../../shared/components/global-header/global-header';
import { GlobalFooter } from '../../shared/components/global-footer/global-footer';
@Component({
    selector: 'app-chart-extractor',
    standalone: true,
    imports: [CommonModule, FormsModule, NgxEchartsModule, GlobalHeader, GlobalFooter],
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

    // ECharts state
    chartOptions: { [key: number]: any } = {};
    echartsInstances: { [key: number]: any } = {};
    
    // Per-chart customizations
    chartSettings: { [key: number]: { palette: string, title: string } } = {};
    
    palettes: { [name: string]: string[] } = {
        default: ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44AF69', '#FCAB10', '#5C4D7D'],
        oceanic: ['#0077b6', '#0096c7', '#48cae4', '#90e0ef', '#ade8f4', '#caf0f8'],
        forest: ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2', '#b7e4c7'],
        sunset: ['#ff7b00', '#ff8800', '#ff9500', '#ffa200', '#ffaa00', '#ffb700'],
        india:  ['#FF9933', '#138808', '#000080', '#FF8C00', '#006400'],
        monochrome: ['#111111', '#333333', '#555555', '#777777', '#999999', '#bbbbbb'],
        pastel: ['#fd7f6f', '#7eb0d5', '#b2e061', '#bd7ebe', '#ffb55a', '#ffee65', '#beb9db', '#fdcce5', '#8bd3c7']
    };

    // Available palettes for UI iteration
    availablePalettes = Object.keys(this.palettes);

    // UI state
    isLoading: boolean = false;
    isExtracting: boolean = false;
    isGenerating: boolean = false;
    hasExtractedData: boolean = false;
    hasCharts: boolean = false;
    errorMessage: string = '';
    successMessage: string = '';
    activeTab: 'input' | 'preview' | 'charts' = 'input';

    // Track which charts have their data panel expanded
    expandedChartData: Set<number> = new Set();

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
                    this.initializeChartSettings();
                    this.updateECharts();
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
                    this.initializeChartSettings();
                    this.updateECharts();
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

    initializeChartSettings(): void {
        this.chartSettings = {};
        this.generatedCharts.forEach((chart, index) => {
            this.chartSettings[index] = {
                palette: 'default',
                title: chart.caption.split(':')[0] || 'Chart'
            };
        });
    }

    updateECharts(): void {
        this.chartOptions = {};

        this.generatedCharts.forEach((chart, index) => {
            const settings = this.chartSettings[index] || { palette: 'default', title: 'Chart' };
            const colors = this.palettes[settings.palette] || this.palettes['default'];

            let option: any = {
                color: colors,
                tooltip: { trigger: 'item' },
                toolbox: {
                    show: true,
                    feature: {
                        saveAsImage: { name: `chart_${index + 1}_${chart.chart_type}` }
                    }
                },
                title: {
                    text: settings.title,
                    left: 'center'
                },
                legend: {
                    top: 'bottom'
                }
            };

            const sourceData = chart.source_data || [];
            
            if (chart.chart_type === 'bar' || chart.chart_type === 'grouped_bar') {
                const xAxisData = sourceData.map(item => Object.values(item)[0]);
                const seriesData = sourceData.map(item => Object.values(item)[1]);
                option.xAxis = { type: 'category', data: xAxisData, axisLabel: { interval: 0, rotate: 30 } };
                option.yAxis = { type: 'value' };
                option.series = [{ data: seriesData, type: 'bar' }];
            } else if (chart.chart_type === 'horizontal_bar') {
                const yAxisData = sourceData.map(item => Object.values(item)[0]);
                const seriesData = sourceData.map(item => Object.values(item)[1]);
                option.xAxis = { type: 'value' };
                option.yAxis = { type: 'category', data: yAxisData };
                option.grid = { left: '3%', right: '4%', bottom: '3%', containLabel: true };
                option.series = [{ data: seriesData, type: 'bar' }];
            } else if (chart.chart_type === 'pie') {
                const pieData = sourceData.map(item => ({ name: Object.values(item)[0], value: Object.values(item)[1] }));
                option.series = [{ type: 'pie', radius: '50%', data: pieData }];
            } else if (chart.chart_type === 'line') {
                const xAxisData = sourceData.map(item => Object.values(item)[0]);
                const seriesData = sourceData.map(item => Object.values(item)[1]);
                option.xAxis = { type: 'category', data: xAxisData };
                option.yAxis = { type: 'value' };
                option.series = [{ data: seriesData, type: 'line', smooth: true }];
            } else if (chart.chart_type === 'big_number') {
                // Approximate a big number by drawing large text in a simple gauge or pie
                // Fallback, we'll just display a simple pie chart of the numbers if any exist
                if(sourceData.length > 0) {
                     const pieData = sourceData.map(item => ({ name: Object.values(item)[0], value: Object.values(item)[1] }));
                     option.series = [{ type: 'pie', radius: ['40%', '70%'], data: pieData }];
                }
            }

            this.chartOptions[index] = option;
            
            // Re-apply option directly if the instance is already initialized
            const ec = this.echartsInstances[index];
            if (ec) {
                ec.setOption(option, true);
            }
        });
    }

    onChartSettingChange(index: number) {
        this.updateECharts();
    }

    onChartInit(ec: any, index: number) {
        this.echartsInstances[index] = ec;
    }

    downloadChart(chart: ChartOutput, index: number): void {
        const ec = this.echartsInstances[index];
        if (ec) {
            const url = ec.getDataURL({ type: 'png', backgroundColor: '#fff', pixelRatio: 2 });
            const filename = `chart_${index + 1}_${chart.chart_type}.png`;
            // ChartService already takes base64 without data type snippet
            const b64 = url.includes(',') ? url.split(',')[1] : url;
            this.chartService.downloadChart(b64, filename);
        } else {
            console.error("EChart instance not ready, attempting fallback...");
            const filename = `chart_${index + 1}_${chart.chart_type}.png`;
            this.chartService.downloadChart(chart.png_base64, filename);
        }
    }

    downloadAllCharts(): void {
        // Build updated base64 instances
        const newCharts = this.generatedCharts.map((c, index) => {
            const ec = this.echartsInstances[index];
            if (ec) {
               const url = ec.getDataURL({ type: 'png', backgroundColor: '#fff', pixelRatio: 2 });
               return { ...c, png_base64: url.includes(',') ? url.split(',')[1] : url };
            }
            return c;
        });

        this.chartService.downloadAllAsZip(newCharts);
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
        this.expandedChartData.clear();
        this.echartsInstances = {};
        this.chartOptions = {};
        this.chartSettings = {};
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
    toggleDarkMode() {
        document.documentElement.classList.toggle('dark');
    }
    toggleDataPreview(index: number): void {
        if (this.expandedChartData.has(index)) {
            this.expandedChartData.delete(index);
        } else {
            this.expandedChartData.add(index);
        }
    }

    isDataExpanded(index: number): boolean {
        return this.expandedChartData.has(index);
    }

    // Get first 5 rows for preview display
    getPreviewData(chart: ChartOutput): Array<{ [key: string]: any }> {
        if (!chart.source_data || chart.source_data.length === 0) return [];
        return chart.source_data.slice(0, 5);
    }

    // Get column headers from source data
    getDataHeaders(chart: ChartOutput): string[] {
        if (!chart.source_data || chart.source_data.length === 0) return [];
        return Object.keys(chart.source_data[0]);
    }

    // Check if there's more data than preview shows
    hasMoreData(chart: ChartOutput): boolean {
        return (chart.source_data?.length || 0) > 5;
    }

    downloadChartDataAsCSV(chart: ChartOutput, index: number): void {
        if (!chart.source_data) return;
        const filename = `chart_${index + 1}_${chart.chart_type}_data`;
        this.chartService.downloadAsCSV(chart.source_data, filename);
        this.successMessage = 'CSV downloaded!';
        setTimeout(() => this.successMessage = '', 2000);
    }

    downloadChartDataAsXLSX(chart: ChartOutput, index: number): void {
        if (!chart.source_data) return;
        const filename = `chart_${index + 1}_${chart.chart_type}_data`;
        this.chartService.downloadAsXLSX(chart.source_data, filename);
        this.successMessage = 'Excel file downloaded!';
        setTimeout(() => this.successMessage = '', 2000);
    }
}
