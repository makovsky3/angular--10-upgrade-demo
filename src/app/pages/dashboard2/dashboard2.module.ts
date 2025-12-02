import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';

// TODO: MaterialAngularSelectModule is not compatible with Angular 19 (Ivy)
// This library was last updated in 2019 and needs to be replaced with a compatible alternative
// import { MaterialAngularSelectModule } from 'material-angular-select';
import { ThemeModule } from 'theme';

import { ChartsModule } from '../charts/charts.module';
import { DashboardModule } from '../dashboard/dashboard.module';
import { MapsModule } from '../maps/maps.module';
import { Dashboard2Component } from './dashboard2.component';
import { FiltersComponent } from './filters/filters.component';

@NgModule({
  imports: [
    CommonModule,
    ThemeModule,
    FormsModule,
    DashboardModule,
    MapsModule,
    ChartsModule,
    // MaterialAngularSelectModule, // Commented out - not compatible with Angular 19
  ],
  declarations: [
    Dashboard2Component,
    FiltersComponent,
  ],
})
export class Dashboard2Module {}
