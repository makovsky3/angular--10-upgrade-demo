import { HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AuthInterceptor, AuthService, FakeBackendInterceptor } from '@services/*';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ChartsModule } from './pages/charts';
import { ComponentsModule } from './pages/components';
import { DashboardModule } from './pages/dashboard';
import { Dashboard2Module } from './pages/dashboard2';
import { FormsModule } from './pages/forms';

@NgModule({ declarations: [AppComponent],
    bootstrap: [AppComponent], imports: [BrowserModule,
        AppRoutingModule,
        ComponentsModule,
        DashboardModule,
        Dashboard2Module,
        FormsModule,
        ChartsModule], providers: [
        AuthService,
        {
            provide: HTTP_INTERCEPTORS,
            useClass: AuthInterceptor,
            multi: true,
        },
        {
            provide: HTTP_INTERCEPTORS,
            useClass: FakeBackendInterceptor,
            multi: true,
        },
        provideHttpClient(withInterceptorsFromDi()),
    ] })
export class AppModule {}
