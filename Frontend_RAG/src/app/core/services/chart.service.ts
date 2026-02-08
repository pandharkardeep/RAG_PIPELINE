import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ExtractedData {
    comparisons: any[];
    breakdowns: any[];
    time_series: any[];
    key_facts: any[];
    tables: any[];
    raw_text: string;
    source_url: string;
}

export interface ChartOutput {
    png_base64: string;
    chart_type: string;
    caption: string;
    alt_text: string;
    data_summary: string;
    source_data?: Array<{ [key: string]: any }>;  // Raw data for CSV/XLSX export
}

export interface ExtractResponse {
    success: boolean;
    extracted_data: ExtractedData;
    data_preview: any[];
    message: string;
}

export interface GenerateResponse {
    success: boolean;
    charts: ChartOutput[];
    message: string;
}

export interface FullPipelineResponse {
    success: boolean;
    extracted_data: ExtractedData;
    charts: ChartOutput[];
    message: string;
}

export interface ChartType {
    id: string;
    name: string;
    description: string;
}

@Injectable({
    providedIn: 'root'
})
export class ChartService {
    private baseUrl = `${environment.apiBaseUrl}/charts`;

    constructor(private http: HttpClient) { }

    /**
     * Extract data from article text or URL
     */
    extractData(text?: string, url?: string): Observable<ExtractResponse> {
        return this.http.post<ExtractResponse>(`${this.baseUrl}/extract`, { text, url });
    }

    /**
     * Generate charts from extracted data
     */
    generateCharts(extractedData: any, chartTypes?: string[]): Observable<GenerateResponse> {
        return this.http.post<GenerateResponse>(`${this.baseUrl}/generate`, {
            extracted_data: extractedData,
            chart_types: chartTypes
        });
    }

    /**
     * Full pipeline: extract data and generate charts
     */
    fullPipeline(text?: string, url?: string, chartTypes?: string[]): Observable<FullPipelineResponse> {
        return this.http.post<FullPipelineResponse>(`${this.baseUrl}/full-pipeline`, {
            text,
            url,
            chart_types: chartTypes
        });
    }

    /**
     * Get available chart types
     */
    getChartTypes(): Observable<{ chart_types: ChartType[] }> {
        return this.http.get<{ chart_types: ChartType[] }>(`${this.baseUrl}/chart-types`);
    }

    /**
     * Convert base64 PNG to downloadable blob
     */
    base64ToBlob(base64: string): Blob {
        const byteString = atob(base64);
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        return new Blob([ab], { type: 'image/png' });
    }

    /**
     * Download chart as PNG
     */
    downloadChart(base64: string, filename: string): void {
        const blob = this.base64ToBlob(base64);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Download all charts as ZIP
     */
    async downloadAllAsZip(charts: ChartOutput[]): Promise<void> {
        // For simplicity, download each chart individually
        // A full ZIP implementation would require JSZip library
        charts.forEach((chart, index) => {
            setTimeout(() => {
                this.downloadChart(chart.png_base64, `chart_${index + 1}_${chart.chart_type}.png`);
            }, index * 500);
        });
    }

    /**
     * Download chart data as CSV
     */
    downloadAsCSV(data: Array<{ [key: string]: any }>, filename: string): void {
        if (!data || data.length === 0) return;

        const headers = Object.keys(data[0]);
        const csvRows = [
            headers.join(','),
            ...data.map(row =>
                headers.map(h => {
                    const val = row[h];
                    // Escape quotes and wrap in quotes if contains comma
                    const strVal = String(val ?? '');
                    return strVal.includes(',') || strVal.includes('"')
                        ? `"${strVal.replace(/"/g, '""')}"`
                        : strVal;
                }).join(',')
            )
        ];

        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename.endsWith('.csv') ? filename : `${filename}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Download chart data as XLSX (using basic XML format)
     */
    downloadAsXLSX(data: Array<{ [key: string]: any }>, filename: string): void {
        if (!data || data.length === 0) return;

        const headers = Object.keys(data[0]);

        // Create simple XML-based Excel format
        let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
        xml += '<?mso-application progid="Excel.Sheet"?>\n';
        xml += '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" ';
        xml += 'xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n';
        xml += '<Worksheet ss:Name="Chart Data">\n<Table>\n';

        // Header row
        xml += '<Row>\n';
        headers.forEach(h => {
            xml += `<Cell><Data ss:Type="String">${this.escapeXml(h)}</Data></Cell>\n`;
        });
        xml += '</Row>\n';

        // Data rows
        data.forEach(row => {
            xml += '<Row>\n';
            headers.forEach(h => {
                const val = row[h];
                const type = typeof val === 'number' ? 'Number' : 'String';
                xml += `<Cell><Data ss:Type="${type}">${this.escapeXml(String(val ?? ''))}</Data></Cell>\n`;
            });
            xml += '</Row>\n';
        });

        xml += '</Table>\n</Worksheet>\n</Workbook>';

        const blob = new Blob([xml], { type: 'application/vnd.ms-excel' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename.endsWith('.xlsx') ? filename : `${filename}.xlsx`;
        a.click();
        URL.revokeObjectURL(url);
    }

    private escapeXml(str: string): string {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&apos;');
    }
}
