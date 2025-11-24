declare const d3: any;
declare const nv: any;

import { Component, HostBinding } from '@angular/core';

@Component({
    template: '',
    standalone: false
})
export abstract class PieChartComponent {
  @HostBinding('class.pie-chart__container') private readonly pieChartContainer = true;
}
