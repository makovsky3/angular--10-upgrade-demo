import { Component, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { BlankLayoutCardComponent } from 'app/components/blank-layout-card';
import { AuthService } from '../../../services/auth';

@Component({
    selector: 'app-login',
    styleUrls: ['../../../components/blank-layout-card/blank-layout-card.component.scss'],
    templateUrl: './login.component.html',
    standalone: false
})
export class LoginComponent extends BlankLayoutCardComponent implements OnInit {
  public loginForm: UntypedFormGroup;
  public email;
  public password;
  public emailPattern = '^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$';
  public error: string;

  constructor(public authService: AuthService,
              public fb: UntypedFormBuilder,
              public router: Router) {
    super();

    this.loginForm = this.fb.group({
      password: new UntypedFormControl('', Validators.required),
      email: new UntypedFormControl('', [
        Validators.required,
        Validators.pattern(this.emailPattern),
        Validators.maxLength(20),
      ]),
    });
    this.email = this.loginForm.get('email');
    this.password = this.loginForm.get('password');
  }

  public ngOnInit() {
    this.authService.logout();
    this.loginForm.valueChanges.subscribe(() => {
      this.error = null;
    });
  }

  public login() {
    this.error = null;
    if (this.loginForm.valid) {
      this.authService.login(this.loginForm.getRawValue())
        .subscribe(res => this.router.navigate(['/app/dashboard']),
                   error => this.error = error.message);
    }
  }

  public onInputChange(event) {
    event.target.required = true;
  }
}
