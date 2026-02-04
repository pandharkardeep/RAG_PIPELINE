import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-thread-formatter',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './thread-formatter.html',
    styleUrl: './thread-formatter.scss'
})
export class ThreadFormatter {
    inputText: string = '';
    formattedThreads: string[] = [];
    maxChars: number = 280;
    isFormatted: boolean = false;

    formatThread(): void {
        if (!this.inputText.trim()) {
            this.formattedThreads = [];
            this.isFormatted = false;
            return;
        }

        // Split text into tweets of max length
        const words = this.inputText.split(' ');
        const tweets: string[] = [];
        let currentTweet = '';

        for (const word of words) {
            if ((currentTweet + ' ' + word).trim().length <= this.maxChars) {
                currentTweet = (currentTweet + ' ' + word).trim();
            } else {
                if (currentTweet) tweets.push(currentTweet);
                currentTweet = word;
            }
        }
        if (currentTweet) tweets.push(currentTweet);

        this.formattedThreads = tweets;
        this.isFormatted = true;
    }

    copyThread(index: number): void {
        const text = `${index + 1}/${this.formattedThreads.length} ${this.formattedThreads[index]}`;
        navigator.clipboard.writeText(text);
    }

    copyAllThreads(): void {
        const fullThread = this.formattedThreads
            .map((t, i) => `${i + 1}/${this.formattedThreads.length} ${t}`)
            .join('\n\n');
        navigator.clipboard.writeText(fullThread);
    }

    clearAll(): void {
        this.inputText = '';
        this.formattedThreads = [];
        this.isFormatted = false;
    }

    get totalChars(): number {
        return this.inputText.length;
    }
}
