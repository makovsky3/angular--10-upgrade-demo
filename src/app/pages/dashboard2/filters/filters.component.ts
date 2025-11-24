import { Component } from '@angular/core';

@Component({
    selector: 'app-filters',
    styleUrls: ['./filters.component.scss'],
    templateUrl: './filters.component.html',
    standalone: false
})
export class FiltersComponent {
  public readonly currencies = ['BYN', 'EUR', 'USD', 'RUR', 'PLN'];
  public currentCurrency = 'BYN';

  public readonly languages = ['Belarusian', 'English', 'USD', 'German', 'Polish'];
  public currentLanguage = 'Belarusian';
}
