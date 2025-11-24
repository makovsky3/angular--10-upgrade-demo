import { Component, HostBinding } from '@angular/core';

@Component({
    selector: 'app-employer-form',
    styleUrls: ['./employer-form.component.scss'],
    templateUrl: 'employer-form.component.html',
    standalone: false
})
export class EmployerFormComponent {
  @HostBinding('class.employer-form') public readonly employerForm = true;
  public qualifications = ['Young Padawan', 'Junior', 'Middle', 'Senior'];
}
