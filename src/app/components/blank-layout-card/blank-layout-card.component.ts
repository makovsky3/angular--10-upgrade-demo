import { Component, HostBinding } from '@angular/core';

import { UpgradableComponent } from 'theme/components/upgradable';

@Component({
    template: '',
    standalone: false
})
export class BlankLayoutCardComponent extends UpgradableComponent {
  @HostBinding('class.blank-layout-card') public readonly blankLayoutCard = true;
}
