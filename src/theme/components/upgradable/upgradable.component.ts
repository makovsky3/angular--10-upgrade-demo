import { AfterViewInit, Component } from '@angular/core';

@Component({
    template: '',
    standalone: false
})
export abstract class UpgradableComponent implements AfterViewInit {
  public ngAfterViewInit() {
    componentHandler.upgradeDom();
  }
}
