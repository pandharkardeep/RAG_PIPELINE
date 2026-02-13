import {
    Component,
    AfterViewInit,
    OnDestroy,
    ElementRef,
    ViewChild,
    NgZone,
    Renderer2
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TopNavbar } from '../../shared/components/top-navbar/top-navbar';

interface NeuralNode {
    x: number;
    y: number;
    vx: number;
    vy: number;
    radius: number;
    pulsePhase: number;
}

interface NeuralEdge {
    from: number;
    to: number;
    pulsePos: number;
    pulseSpeed: number;
    active: boolean;
}

@Component({
    selector: 'app-landing',
    standalone: true,
    imports: [CommonModule, RouterLink, TopNavbar],
    templateUrl: './landing.html',
    styleUrl: './landing.scss'
})
export class Landing implements AfterViewInit, OnDestroy {
    @ViewChild('neuralCanvas', { static: false }) canvasRef!: ElementRef<HTMLCanvasElement>;

    isDarkMode = true;
    private animationId: number | null = null;
    private nodes: NeuralNode[] = [];
    private edges: NeuralEdge[] = [];
    private ctx: CanvasRenderingContext2D | null = null;
    private canvasWidth = 0;
    private canvasHeight = 0;
    private resizeObserver: ResizeObserver | null = null;

    features = [
        {
            icon: 'twitter',
            title: 'Tweet Generator',
            description: 'Viral-ready tweets crafted from any article using neural AI instantly.',
            color: '#1DA1F2',
            delay: '0s'
        },
        {
            icon: 'thread',
            title: 'Thread Formatter',
            description: 'Long-form content transformed into captivating Twitter threads.',
            color: '#A855F7',
            delay: '0.1s'
        },
        {
            icon: 'chart',
            title: 'Chart Extractor',
            description: 'Auto-generate publication-ready charts and infographics from data.',
            color: '#22C55E',
            delay: '0.2s'
        },
        {
            icon: 'search',
            title: 'Research Assistant',
            description: 'AI-powered summaries, deep analysis, and comprehensive reports.',
            color: '#3B82F6',
            delay: '0.3s'
        }
    ];

    steps = [
        {
            number: '01',
            icon: '📋',
            title: 'Paste Your Content',
            description: 'Drop in any article URL or paste your text directly into Queryflow'
        },
        {
            number: '02',
            icon: '🧠',
            title: 'Neural AI Processing',
            description: 'Our neural network analyzes, extracts key insights, and generates content'
        },
        {
            number: '03',
            icon: '🚀',
            title: 'Share & Shine',
            description: 'Get polished, ready-to-post content in multiple formats instantly'
        }
    ];

    constructor(private ngZone: NgZone, private renderer: Renderer2) {
        // Initialize theme from body attribute
        const theme = document.body.getAttribute('data-theme');
        this.isDarkMode = theme !== 'light';
    }

    toggleTheme(): void {
        this.isDarkMode = !this.isDarkMode;
        this.renderer.setAttribute(document.body, 'data-theme', this.isDarkMode ? 'dark' : 'light');
    }

    ngAfterViewInit(): void {
        this.initCanvas();
    }

    ngOnDestroy(): void {
        if (this.animationId !== null) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
    }

    private initCanvas(): void {
        if (!this.canvasRef) return;
        const canvas = this.canvasRef.nativeElement;
        this.ctx = canvas.getContext('2d');
        if (!this.ctx) return;

        this.resizeCanvas();

        // Watch for resize
        this.resizeObserver = new ResizeObserver(() => this.resizeCanvas());
        this.resizeObserver.observe(canvas.parentElement!);

        this.createNodes();
        this.createEdges();

        // Run animation outside Angular zone for performance
        this.ngZone.runOutsideAngular(() => this.animate());
    }

    private resizeCanvas(): void {
        const canvas = this.canvasRef.nativeElement;
        const parent = canvas.parentElement!;
        const dpr = window.devicePixelRatio || 1;
        this.canvasWidth = parent.clientWidth;
        this.canvasHeight = parent.clientHeight;
        canvas.width = this.canvasWidth * dpr;
        canvas.height = this.canvasHeight * dpr;
        canvas.style.width = this.canvasWidth + 'px';
        canvas.style.height = this.canvasHeight + 'px';
        this.ctx?.scale(dpr, dpr);

        // Regenerate nodes on resize
        if (this.nodes.length > 0) {
            this.createNodes();
            this.createEdges();
        }
    }

    private createNodes(): void {
        const count = Math.min(Math.floor((this.canvasWidth * this.canvasHeight) / 18000), 80);
        this.nodes = [];
        for (let i = 0; i < count; i++) {
            this.nodes.push({
                x: Math.random() * this.canvasWidth,
                y: Math.random() * this.canvasHeight,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                radius: Math.random() * 2 + 1.5,
                pulsePhase: Math.random() * Math.PI * 2
            });
        }
    }

    private createEdges(): void {
        this.edges = [];
        const maxDist = 180;
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const dx = this.nodes[i].x - this.nodes[j].x;
                const dy = this.nodes[i].y - this.nodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < maxDist) {
                    this.edges.push({
                        from: i,
                        to: j,
                        pulsePos: Math.random(),
                        pulseSpeed: 0.002 + Math.random() * 0.004,
                        active: Math.random() > 0.6
                    });
                }
            }
        }
    }

    private animate(): void {
        if (!this.ctx) return;
        const ctx = this.ctx;
        const w = this.canvasWidth;
        const h = this.canvasHeight;

        ctx.clearRect(0, 0, w, h);

        // Get current theme colors from CSS custom properties
        const style = getComputedStyle(document.body);
        const nodeColor = style.getPropertyValue('--canvas-node').trim() || 'rgba(99,102,241,0.6)';
        const edgeColor = style.getPropertyValue('--canvas-edge').trim() || 'rgba(99,102,241,0.12)';
        const pulseColor = style.getPropertyValue('--canvas-pulse').trim() || 'rgba(34,211,238,0.8)';

        // Update and draw edges
        for (const edge of this.edges) {
            const a = this.nodes[edge.from];
            const b = this.nodes[edge.to];
            const dx = a.x - b.x;
            const dy = a.y - b.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist > 200) continue;

            const opacity = 1 - dist / 200;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = edgeColor;
            ctx.globalAlpha = opacity * 1.5;
            ctx.lineWidth = 1.2;
            ctx.stroke();
            ctx.globalAlpha = 1;

            // Animated pulse traveling along edge
            if (edge.active) {
                edge.pulsePos += edge.pulseSpeed;
                if (edge.pulsePos > 1) {
                    edge.pulsePos = 0;
                    edge.active = Math.random() > 0.3;
                }
                const px = a.x + (b.x - a.x) * edge.pulsePos;
                const py = a.y + (b.y - a.y) * edge.pulsePos;

                ctx.beginPath();
                ctx.arc(px, py, 2, 0, Math.PI * 2);
                ctx.fillStyle = pulseColor;
                ctx.globalAlpha = opacity * 0.9;
                ctx.fill();
                ctx.globalAlpha = 1;
            } else if (Math.random() > 0.998) {
                edge.active = true;
                edge.pulsePos = 0;
            }
        }

        // Update and draw nodes
        const time = Date.now() * 0.001;
        for (const node of this.nodes) {
            node.x += node.vx;
            node.y += node.vy;

            // Bounce off edges
            if (node.x < 0 || node.x > w) node.vx *= -1;
            if (node.y < 0 || node.y > h) node.vy *= -1;
            node.x = Math.max(0, Math.min(w, node.x));
            node.y = Math.max(0, Math.min(h, node.y));

            const pulse = Math.sin(time * 2 + node.pulsePhase) * 0.3 + 0.7;

            // Node glow
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.radius * 3, 0, Math.PI * 2);
            const gradient = ctx.createRadialGradient(
                node.x, node.y, 0,
                node.x, node.y, node.radius * 3
            );
            gradient.addColorStop(0, pulseColor);
            gradient.addColorStop(1, 'transparent');
            ctx.fillStyle = gradient;
            ctx.globalAlpha = pulse * 0.2;
            ctx.fill();
            ctx.globalAlpha = 1;

            // Node core
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            ctx.fillStyle = nodeColor;
            ctx.globalAlpha = pulse;
            ctx.fill();
            ctx.globalAlpha = 1;
        }

        // Rebuild edges periodically (every ~3 seconds worth of frames)
        if (Math.random() < 0.005) {
            this.createEdges();
        }

        this.animationId = requestAnimationFrame(() => this.animate());
    }
}
