import { Component } from '@angular/core';

import { UpgradableComponent } from 'theme/components/upgradable';

@Component({
    selector: 'app-tables',
    templateUrl: './right-sidebar.component.html',
    styleUrls: ['./right-sidebar.component.scss'],
    standalone: false
})
export class RightSidebarComponent extends UpgradableComponent {}
