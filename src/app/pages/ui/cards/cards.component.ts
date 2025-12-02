import { Component, HostBinding } from '@angular/core';

import { UpgradableComponent } from 'theme/components/upgradable';

@Component({
    selector: 'app-cards',
    templateUrl: './cards.component.html',
    styleUrls: ['./cards.component.scss'],
    standalone: false
})
export class CardsComponent extends UpgradableComponent {
  @HostBinding('class.mdl-grid') public readonly mdlGrid = true;
  @HostBinding('class.ui-cards') public readonly uiCards = true;
}
