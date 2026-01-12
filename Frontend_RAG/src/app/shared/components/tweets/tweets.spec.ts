import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Tweets } from './tweets';

describe('Tweets', () => {
    let component: Tweets;
    let fixture: ComponentFixture<Tweets>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [Tweets]
        }).compileComponents();

        fixture = TestBed.createComponent(Tweets);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
