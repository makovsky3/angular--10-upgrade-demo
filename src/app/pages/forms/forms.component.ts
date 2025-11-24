import { Component } from '@angular/core';

import { UpgradableComponent } from 'theme/components/upgradable';

@Component({
    selector: 'app-forms',
    template: `<app-employer-form></app-employer-form>`,
    standalone: false
})
export class FormsComponent extends UpgradableComponent { }
