import { Component, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '@services/*';

import { BlankLayoutCardComponent } from 'app/components/blank-layout-card';

@Component({
    selector: 'app-sign-up',
    styleUrls: ['../../../components/blank-layout-card/blank-layout-card.component.scss'],
    templateUrl: './sign-up.component.html',
    standalone: false
})
export class SignUpComponent extends BlankLayoutCardComponent implements OnInit {

  public signupForm: UntypedFormGroup;
  public email;
  public password;
  public username;
  public emailPattern = '^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$';
  public error: string;

  constructor(public authService: AuthService,
              public fb: UntypedFormBuilder,
              public router: Router) {
    super();

    this.signupForm = this.fb.group({
      password: new UntypedFormControl('', Validators.required),
      email: new UntypedFormControl('', [
        Validators.required,
        Validators.pattern(this.emailPattern),
        Validators.maxLength(20),
      ]),
      username: new UntypedFormControl('', [Validators.required, Validators.maxLength(10)]),
    });
    this.email = this.signupForm.get('email');
    this.password = this.signupForm.get('password');
    this.username = this.signupForm.get('username');
  }

  public ngOnInit() {
    this.authService.logout();
    this.signupForm.valueChanges.subscribe(() => {
      this.error = null;
    });
  }

  public login() {
    this.error = null;
    if (this.signupForm.valid) {
      this.authService.signup(this.signupForm.getRawValue())
        .subscribe(res => this.router.navigate(['/app/dashboard']),
                   error => this.error = error.message);
    }
  }

  public onInputChange(event) {
    event.target.required = true;
  }
}
