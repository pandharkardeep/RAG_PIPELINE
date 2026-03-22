import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-global-header',
  imports: [],
  templateUrl: './global-header.html',
  styleUrl: './global-header.scss'
})
export class GlobalHeader {
  @Input() title: string = 'Research Hub';
}
