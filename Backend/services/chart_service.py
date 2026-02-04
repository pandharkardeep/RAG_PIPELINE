import io
import base64
from typing import Optional, List, Tuple
from dataclasses import dataclass, asdict
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFont
from models.ChartModels import ChartResult

class ChartService:
    """
    Service for generating Twitter-optimized charts
    """
    
    # Twitter-optimized dimensions
    CHART_WIDTH = 1200
    CHART_HEIGHT = 675
    DPI = 100
    
    # Professional color palette
    COLORS = [
        '#2E86AB',  # Steel blue
        '#A23B72',  # Raspberry
        '#F18F01',  # Orange
        '#C73E1D',  # Red
        '#3B1F2B',  # Dark purple
        '#44AF69',  # Green
        '#FCAB10',  # Gold
        '#5C4D7D',  # Purple
    ]
    
    # India-themed accent colors (optional)
    INDIA_COLORS = ['#FF9933', '#138808', '#000080']  # Saffron, Green, Navy
    
    def __init__(self):
        # Set up matplotlib styling
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette(self.COLORS)
        
        # Configure font
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'DejaVu Sans', 'Helvetica', 'sans-serif'],
            'font.size': 14,
            'axes.titlesize': 20,
            'axes.labelsize': 14,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 12,
            'figure.titlesize': 24,
            'axes.spines.top': False,
            'axes.spines.right': False,
        })
        
        print("ChartService initialized")
    
    def infer_chart_type(self, data: dict) -> str:
        """
        Infer the best chart type based on data characteristics
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            Chart type string: 'bar', 'horizontal_bar', 'pie', 'line', 'big_number', 'grouped_bar'
        """
        # Check for comparisons (bar charts)
        if data.get('comparisons'):
            comp = data['comparisons'][0]
            entities = comp.get('entities', {})
            if len(entities) <= 6:
                return 'horizontal_bar'
            else:
                return 'bar'
        
        # Check for breakdowns (pie/donut for percentages ~100)
        if data.get('breakdowns'):
            bd = data['breakdowns'][0]
            values = bd.get('values', {})
            total = sum(values.values()) if values else 0
            if 90 <= total <= 110:  # Approximately 100%
                return 'pie'
            else:
                return 'bar'
        
        # Check for time series (line charts)
        if data.get('time_series'):
            return 'line'
        
        # Check for key facts (big number infographic)
        if data.get('key_facts'):
            return 'big_number'
        
        return 'bar'  # Default
    
    def generate_chart(self, data: dict, chart_type: str = None) -> ChartResult:
        """
        Generate a chart from extracted data
        
        Args:
            data: Extracted data dictionary
            chart_type: Optional chart type override
            
        Returns:
            ChartResult with PNG base64 and metadata
        """
        if chart_type is None:
            chart_type = self.infer_chart_type(data)
        
        # Route to appropriate generator
        generators = {
            'bar': self._generate_bar_chart,
            'horizontal_bar': self._generate_horizontal_bar_chart,
            'pie': self._generate_pie_chart,
            'line': self._generate_line_chart,
            'big_number': self._generate_big_number,
            'grouped_bar': self._generate_grouped_bar_chart,
        }
        
        generator = generators.get(chart_type, self._generate_bar_chart)
        return generator(data, chart_type)
    
    def generate_all_charts(self, data: dict) -> List[ChartResult]:
        """
        Generate multiple charts from all extractable data
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            List of ChartResult objects
        """
        charts = []
        
        # Generate chart for each comparison
        for i, comp in enumerate(data.get('comparisons', [])[:3]):
            comp_data = {'comparisons': [comp]}
            charts.append(self._generate_horizontal_bar_chart(comp_data, 'horizontal_bar'))
        
        # Generate chart for each breakdown
        for bd in data.get('breakdowns', [])[:2]:
            bd_data = {'breakdowns': [bd]}
            values = bd.get('values', {})
            total = sum(values.values()) if values else 0
            if 90 <= total <= 110:
                charts.append(self._generate_pie_chart(bd_data, 'pie'))
            else:
                charts.append(self._generate_bar_chart(bd_data, 'bar'))
        
        # Generate chart for each time series
        for ts in data.get('time_series', [])[:2]:
            ts_data = {'time_series': [ts]}
            charts.append(self._generate_line_chart(ts_data, 'line'))
        
        # Generate big number for key facts (max 1)
        if data.get('key_facts') and len(charts) < 5:
            kf_data = {'key_facts': data['key_facts'][:3]}
            charts.append(self._generate_big_number(kf_data, 'big_number'))
        
        return charts[:5]  # Max 5 charts
    
    def _generate_horizontal_bar_chart(self, data: dict, chart_type: str) -> ChartResult:
        """Generate horizontal bar chart for comparisons"""
        fig, ax = plt.subplots(figsize=(self.CHART_WIDTH/self.DPI, self.CHART_HEIGHT/self.DPI), dpi=self.DPI)
        
        comp = data['comparisons'][0]
        entities = comp.get('entities', {})
        metric = comp.get('metric', 'Value')
        unit = comp.get('unit', '')
        
        categories = list(entities.keys())
        values = list(entities.values())
        
        # Create horizontal bar chart
        colors = self.COLORS[:len(categories)]
        bars = ax.barh(categories, values, color=colors, height=0.6, edgecolor='white', linewidth=1)
        
        # Add data labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height()/2,
                    f'{val}{unit}', va='center', ha='left', fontsize=14, fontweight='bold')
        
        # Styling
        ax.set_xlabel(f'{metric.title()} {f"({unit})" if unit else ""}', fontsize=14)
        ax.set_title(metric.title(), fontsize=20, fontweight='bold', pad=20)
        ax.set_xlim(0, max(values) * 1.3)
        
        # Minimal gridlines
        ax.xaxis.grid(True, alpha=0.3)
        ax.yaxis.grid(False)
        
        # Add source footer
        source_snippet = comp.get('source_snippet', '')[:80]
        if source_snippet:
            fig.text(0.02, 0.02, f'Source: {source_snippet}...', fontsize=9, alpha=0.6)
        
        plt.tight_layout(rect=[0, 0.05, 1, 1])
        
        # Convert to base64
        png_base64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        # Generate caption and alt text
        comparison_text = ', '.join([f'{k}: {v}{unit}' for k, v in entities.items()])
        caption = f"📊 {metric.title()}: {comparison_text}"
        alt_text = f"Horizontal bar chart comparing {metric}. {comparison_text}."
        
        return ChartResult(
            png_base64=png_base64,
            chart_type=chart_type,
            caption=caption[:280],
            alt_text=alt_text,
            data_summary=comparison_text
        )
    
    def _generate_bar_chart(self, data: dict, chart_type: str) -> ChartResult:
        """Generate vertical bar chart"""
        fig, ax = plt.subplots(figsize=(self.CHART_WIDTH/self.DPI, self.CHART_HEIGHT/self.DPI), dpi=self.DPI)
        
        # Handle both comparisons and breakdowns
        if data.get('comparisons'):
            source = data['comparisons'][0]
            entities = source.get('entities', {})
            title = source.get('metric', 'Comparison')
        elif data.get('breakdowns'):
            source = data['breakdowns'][0]
            entities = source.get('values', {})
            title = source.get('category', 'Breakdown')
        else:
            return self._generate_empty_chart("No data available")
        
        unit = source.get('unit', '')
        categories = list(entities.keys())
        values = list(entities.values())
        
        # Create bar chart
        colors = self.COLORS[:len(categories)]
        bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='white', linewidth=1)
        
        # Add data labels on top
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values) * 0.02,
                    f'{val}{unit}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Styling
        ax.set_ylabel(f'Value {f"({unit})" if unit else ""}', fontsize=14)
        ax.set_title(title.title(), fontsize=20, fontweight='bold', pad=20)
        ax.set_ylim(0, max(values) * 1.2)
        
        # Rotate x labels if needed
        if len(categories) > 4:
            plt.xticks(rotation=45, ha='right')
        
        ax.yaxis.grid(True, alpha=0.3)
        ax.xaxis.grid(False)
        
        plt.tight_layout()
        
        png_base64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        summary = ', '.join([f'{k}: {v}{unit}' for k, v in entities.items()])
        caption = f"📊 {title.title()}: {summary[:200]}"
        alt_text = f"Bar chart showing {title}. {summary}."
        
        return ChartResult(
            png_base64=png_base64,
            chart_type=chart_type,
            caption=caption[:280],
            alt_text=alt_text,
            data_summary=summary
        )
    
    def _generate_pie_chart(self, data: dict, chart_type: str) -> ChartResult:
        """Generate pie/donut chart for percentage breakdowns"""
        fig, ax = plt.subplots(figsize=(self.CHART_WIDTH/self.DPI, self.CHART_HEIGHT/self.DPI), dpi=self.DPI)
        
        bd = data['breakdowns'][0]
        values_dict = bd.get('values', {})
        title = bd.get('category', 'Breakdown')
        unit = bd.get('unit', '%')
        
        labels = list(values_dict.keys())
        values = list(values_dict.values())
        colors = self.COLORS[:len(labels)]
        
        # Create donut chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            pctdistance=0.75,
            wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
        )
        
        # Style autopct text
        for autotext in autotexts:
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        
        ax.set_title(title.title(), fontsize=20, fontweight='bold', pad=20)
        
        # Add center text
        ax.text(0, 0, f'Total\n100{unit}', ha='center', va='center', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        png_base64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        summary = ', '.join([f'{k}: {v}{unit}' for k, v in values_dict.items()])
        caption = f"🥧 {title.title()}: {summary[:200]}"
        alt_text = f"Pie chart showing {title}. {summary}."
        
        return ChartResult(
            png_base64=png_base64,
            chart_type=chart_type,
            caption=caption[:280],
            alt_text=alt_text,
            data_summary=summary
        )
    
    def _generate_line_chart(self, data: dict, chart_type: str) -> ChartResult:
        """Generate line chart for time series data"""
        fig, ax = plt.subplots(figsize=(self.CHART_WIDTH/self.DPI, self.CHART_HEIGHT/self.DPI), dpi=self.DPI)
        
        ts = data['time_series'][0]
        ts_data = ts.get('data', [])
        title = ts.get('label', 'Time Series')
        unit = ts.get('unit', '')
        
        years = [d.get('year', d.get('x', i)) for i, d in enumerate(ts_data)]
        values = [d.get('value', d.get('y', 0)) for d in ts_data]
        
        # Create line chart with markers
        ax.plot(years, values, color=self.COLORS[0], linewidth=3, marker='o', markersize=10)
        ax.fill_between(years, values, alpha=0.2, color=self.COLORS[0])
        
        # Add data labels
        for x, y in zip(years, values):
            ax.annotate(f'{y}{unit}', (x, y), textcoords="offset points", 
                       xytext=(0, 10), ha='center', fontsize=11, fontweight='bold')
        
        # Styling
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel(f'{title} {f"({unit})" if unit else ""}', fontsize=14)
        ax.set_title(title.title(), fontsize=20, fontweight='bold', pad=20)
        
        ax.yaxis.grid(True, alpha=0.3)
        ax.xaxis.grid(False)
        
        plt.tight_layout()
        
        png_base64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        start_val = values[0] if values else 0
        end_val = values[-1] if values else 0
        change = ((end_val - start_val) / start_val * 100) if start_val else 0
        
        caption = f"📈 {title}: From {start_val}{unit} to {end_val}{unit} ({change:+.1f}% change)"
        alt_text = f"Line chart showing {title} over time from {years[0] if years else 'start'} to {years[-1] if years else 'end'}."
        
        return ChartResult(
            png_base64=png_base64,
            chart_type=chart_type,
            caption=caption[:280],
            alt_text=alt_text,
            data_summary=f"{years[0]}: {start_val} → {years[-1]}: {end_val}" if years else ""
        )
    
    def _generate_big_number(self, data: dict, chart_type: str) -> ChartResult:
        """Generate big number infographic for key facts"""
        # Create image with Pillow for more control
        img = Image.new('RGB', (self.CHART_WIDTH, self.CHART_HEIGHT), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        facts = data.get('key_facts', [])[:3]
        
        if not facts:
            return self._generate_empty_chart("No key facts available")
        
        # Use system fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 72)
            subtitle_font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        y_offset = 80
        
        for i, fact in enumerate(facts):
            value = fact.get('value', fact) if isinstance(fact, dict) else str(fact)
            label = fact.get('fact', '') if isinstance(fact, dict) else ''
            context = fact.get('context', '') if isinstance(fact, dict) else ''
            
            # Draw value
            draw.text((self.CHART_WIDTH // 2, y_offset), str(value), 
                     font=title_font, fill='#f8f8f2', anchor='mt')
            
            # Draw label
            draw.text((self.CHART_WIDTH // 2, y_offset + 80), label, 
                     font=subtitle_font, fill='#bd93f9', anchor='mt')
            
            # Draw context
            if context:
                draw.text((self.CHART_WIDTH // 2, y_offset + 130), context, 
                         font=small_font, fill='#6272a4', anchor='mt')
            
            y_offset += 200
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        png_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        fact_texts = [f"{f.get('fact', '')}: {f.get('value', '')}" if isinstance(f, dict) else str(f) for f in facts]
        summary = '. '.join(fact_texts)
        
        caption = f"💡 Key Stats: {summary[:250]}"
        alt_text = f"Infographic showing key statistics: {summary}"
        
        return ChartResult(
            png_base64=png_base64,
            chart_type=chart_type,
            caption=caption[:280],
            alt_text=alt_text,
            data_summary=summary
        )
    
    def _generate_grouped_bar_chart(self, data: dict, chart_type: str) -> ChartResult:
        """Generate grouped bar chart for multi-metric comparisons"""
        # For now, fallback to horizontal bar
        return self._generate_horizontal_bar_chart(data, chart_type)
    
    def _generate_empty_chart(self, message: str) -> ChartResult:
        """Generate placeholder chart when no data available"""
        fig, ax = plt.subplots(figsize=(self.CHART_WIDTH/self.DPI, self.CHART_HEIGHT/self.DPI), dpi=self.DPI)
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=24, transform=ax.transAxes)
        ax.axis('off')
        
        png_base64 = self._fig_to_base64(fig)
        plt.close(fig)
        
        return ChartResult(
            png_base64=png_base64,
            chart_type='empty',
            caption=message,
            alt_text=message,
            data_summary=""
        )
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 PNG"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=self.DPI, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
