import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule as NgFormsModule } from '@angular/forms';
// TODO: MaterialAngularSelectModule is not compatible with Angular 19 (Ivy)
// import { MaterialAngularSelectModule } from 'material-angular-select';

import { ThemeModule } from 'theme';

import { EmployerFormComponent } from './employer-form';
import { FormsComponent } from './forms.component';

@NgModule({
  imports: [
    CommonModule,
    ThemeModule,
    NgFormsModule,
    // MaterialAngularSelectModule, // Commented out - not compatible with Angular 19
  ],
  declarations: [
    FormsComponent,
    EmployerFormComponent,
  ],
  providers: [],
})
export class FormsModule { }
