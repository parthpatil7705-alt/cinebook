"""
Management command to seed CineBook with sample data.
Creates admin user, movies, theaters, shows, and sample bookings.
"""
import random
from datetime import timedelta, date, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed CineBook with sample data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Generate full dataset with 100K+ bookings for performance testing',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🎬 Seeding CineBook database...'))

        self.create_admin()
        self.create_users()
        genres = self.create_genres()
        languages = self.create_languages()
        cast_members = self.create_cast()
        movies = self.create_movies(genres, languages, cast_members)
        cities = self.create_cities()
        categories = self.create_seat_categories()
        theaters = self.create_theaters(cities)
        screens = self.create_screens(theaters, categories)
        shows = self.create_shows(movies, screens, categories)

        if options['full']:
            self.create_bulk_bookings(shows, 100000)
        else:
            self.create_sample_bookings(shows)

        self.stdout.write(self.style.SUCCESS('✅ CineBook seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('Admin credentials: admin / CineBook@Admin2026'))

    def create_admin(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@cinebook.local',
                password='CineBook@Admin2026',
                first_name='Admin',
                last_name='User',
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Admin user created'))
        else:
            self.stdout.write('  → Admin user already exists')

    def create_users(self):
        users_data = [
            ('john_doe', 'john@example.com', 'John', 'Doe', 'Test@1234'),
            ('jane_smith', 'jane@example.com', 'Jane', 'Smith', 'Test@1234'),
            ('raj_kumar', 'raj@example.com', 'Raj', 'Kumar', 'Test@1234'),
            ('priya_sharma', 'priya@example.com', 'Priya', 'Sharma', 'Test@1234'),
            ('mike_wilson', 'mike@example.com', 'Mike', 'Wilson', 'Test@1234'),
        ]
        for username, email, first, last, password in users_data:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username, email=email, password=password,
                    first_name=first, last_name=last,
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(users_data)} sample users created'))

    def create_genres(self):
        from apps.movies.models import Genre
        genres_data = [
            ('Action', 'action', 'fas fa-bolt'),
            ('Comedy', 'comedy', 'fas fa-laugh'),
            ('Drama', 'drama', 'fas fa-theater-masks'),
            ('Horror', 'horror', 'fas fa-ghost'),
            ('Romance', 'romance', 'fas fa-heart'),
            ('Sci-Fi', 'sci-fi', 'fas fa-rocket'),
            ('Thriller', 'thriller', 'fas fa-skull'),
            ('Animation', 'animation', 'fas fa-palette'),
            ('Adventure', 'adventure', 'fas fa-compass'),
            ('Fantasy', 'fantasy', 'fas fa-hat-wizard'),
        ]
        genres = []
        for name, slug, icon in genres_data:
            genre, _ = Genre.objects.get_or_create(
                slug=slug, defaults={'name': name, 'icon': icon}
            )
            genres.append(genre)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(genres)} genres created'))
        return genres

    def create_languages(self):
        from apps.movies.models import Language
        languages_data = [
            ('English', 'en'), ('Hindi', 'hi'), ('Tamil', 'ta'),
            ('Telugu', 'te'), ('Malayalam', 'ml'), ('Kannada', 'kn'),
        ]
        languages = []
        for name, code in languages_data:
            lang, _ = Language.objects.get_or_create(
                code=code, defaults={'name': name}
            )
            languages.append(lang)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(languages)} languages created'))
        return languages

    def create_cast(self):
        from apps.movies.models import CastMember
        cast_data = [
            ('Shah Rukh Khan', 'actor'), ('Aamir Khan', 'actor'),
            ('Deepika Padukone', 'actor'), ('Ranveer Singh', 'actor'),
            ('Rajkumar Hirani', 'director'), ('S.S. Rajamouli', 'director'),
            ('Christopher Nolan', 'director'), ('Alia Bhatt', 'actor'),
            ('Prabhas', 'actor'), ('Vijay Thalapathy', 'actor'),
            ('Nayanthara', 'actor'), ('Sanjay Leela Bhansali', 'director'),
            ('Atlee', 'director'), ('Karan Johar', 'producer'),
            ('Dhanush', 'actor'), ('Ranbir Kapoor', 'actor'),
        ]
        members = []
        for name, role_type in cast_data:
            member, _ = CastMember.objects.get_or_create(
                name=name, defaults={
                    'role_type': role_type,
                    'bio': f'{name} is a renowned {role_type} in the Indian film industry.'
                }
            )
            members.append(member)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(members)} cast members created'))
        return members

    def create_movies(self, genres, languages, cast_members):
        from apps.movies.models import Movie, MovieCast
        movies_data = [
            {
                'title': 'Galactic Storm',
                'slug': 'galactic-storm',
                'description': 'In a distant galaxy, a group of rebel fighters must unite against an overwhelming empire threatening to destroy their home worlds. With breathtaking space battles and emotional character arcs, this epic sci-fi adventure redefines the genre.',
                'duration': timedelta(hours=2, minutes=45),
                'release_date': date.today() - timedelta(days=5),
                'age_certification': 'UA',
                'trailer_youtube_id': 'dQw4w9WgXcQ',
                'genres': [0, 5, 8],  # Action, Sci-Fi, Adventure
                'languages': [0, 1],  # English, Hindi
                'cast': [0, 2, 6],
            },
            {
                'title': 'The Last Laugh',
                'slug': 'the-last-laugh',
                'description': 'A washed-up comedian gets one last chance at redemption when a viral video catapults him back into the spotlight. But fame comes with a price in this heartwarming comedy-drama.',
                'duration': timedelta(hours=2, minutes=10),
                'release_date': date.today() - timedelta(days=14),
                'age_certification': 'U',
                'trailer_youtube_id': 'dQw4w9WgXcQ',
                'genres': [1, 2],  # Comedy, Drama
                'languages': [0, 1],
                'cast': [0, 3, 4],
            },
            {
                'title': 'Whispers in the Dark',
                'slug': 'whispers-in-the-dark',
                'description': 'A family moves into an ancestral mansion only to discover that the walls hold terrifying secrets. As supernatural events escalate, they must uncover the truth before it consumes them.',
                'duration': timedelta(hours=2, minutes=5),
                'release_date': date.today() - timedelta(days=3),
                'age_certification': 'A',
                'trailer_youtube_id': 'dQw4w9WgXcQ',
                'genres': [3, 6],  # Horror, Thriller
                'languages': [1],  # Hindi
                'cast': [7, 15, 11],
            },
            {
                'title': 'Eternal Monsoon',
                'slug': 'eternal-monsoon',
                'description': 'Set against the backdrop of Mumbai monsoons, two strangers find love in unexpected places. A beautiful romance that explores the complexities of modern relationships.',
                'duration': timedelta(hours=2, minutes=20),
                'release_date': date.today() - timedelta(days=10),
                'age_certification': 'UA',
                'trailer_youtube_id': 'dQw4w9WgXcQ',
                'genres': [4, 2],  # Romance, Drama
                'languages': [1],  # Hindi
                'cast': [3, 7, 11],
            },
            {
                'title': 'RRR 2: Rise Again',
                'slug': 'rrr-2-rise-again',
                'description': 'The epic sequel to the blockbuster RRR. Two legendary warriors must reunite to face an ancient evil that threatens the entire subcontinent. Packed with jaw-dropping action sequences.',
                'duration': timedelta(hours=3, minutes=0),
                'release_date': date.today() + timedelta(days=7),
                'age_certification': 'UA',
                'trailer_youtube_id': 'dQw4w9WgXcQ',
                'genres': [0, 2, 8],  # Action, Drama, Adventure
                'languages': [1, 3],  # Hindi, Telugu
                'cast': [8, 5, 3],
            },
            {
                'title': 'Code Breaker',
                'slug': 'code-breaker',
                'description': 'A brilliant cryptographer discovers a pattern in global financial markets that could destabilize the world economy. A race against time thriller that keeps you on the edge.',
                'duration': timedelta(hours=2, minutes=15),
                'release_date': date.today() - timedelta(days=1),
                'age_certification': 'UA',
                'trailer_youtube_id': 'dQw4w9WgXcQ',
                'genres': [6, 0],  # Thriller, Action
                'languages': [0],  # English
                'cast': [6, 2, 14],
            },
            {
                'title': 'The Magic Kingdom',
                'slug': 'the-magic-kingdom',
                'description': 'A young girl discovers a portal to a magical world where mythical creatures are real. An enchanting animated film for the whole family.',
                'duration': timedelta(hours=1, minutes=50),
                'release_date': date.today() - timedelta(days=20),
                'age_certification': 'U',
                'trailer_youtube_id': 'dQw4w9WgXcQ',
                'genres': [7, 9],  # Animation, Fantasy
                'languages': [0, 1],
                'cast': [10, 13],
            },
            {
                'title': 'Vikram Returns',
                'slug': 'vikram-returns',
                'description': 'The undercover agent is back with a mission more dangerous than ever. Tamil cinema\'s biggest action franchise continues with explosive sequences and an intricate plot.',
                'duration': timedelta(hours=2, minutes=40),
                'release_date': date.today() - timedelta(days=7),
                'age_certification': 'UA',
                'trailer_youtube_id': 'dQw4w9WgXcQ',
                'genres': [0, 6],  # Action, Thriller
                'languages': [2, 1],  # Tamil, Hindi
                'cast': [9, 14, 12],
            },
        ]

        movies = []
        for data in movies_data:
            movie, created = Movie.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'title': data['title'],
                    'description': data['description'],
                    'duration': data['duration'],
                    'release_date': data['release_date'],
                    'age_certification': data['age_certification'],
                    'trailer_youtube_id': data['trailer_youtube_id'],
                    'is_active': True,
                    'avg_rating': Decimal(str(round(random.uniform(3.0, 4.8), 2))),
                    'total_ratings': random.randint(10, 500),
                }
            )
            if created:
                movie.genres.set([genres[i] for i in data['genres']])
                movie.languages.set([languages[i] for i in data['languages']])
                for idx, cast_idx in enumerate(data['cast']):
                    MovieCast.objects.get_or_create(
                        movie=movie, cast_member=cast_members[cast_idx],
                        defaults={'character_name': f'Character {idx + 1}', 'order': idx}
                    )
            movies.append(movie)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(movies)} movies created'))
        return movies

    def create_cities(self):
        from apps.theaters.models import City
        cities_data = [
            ('Mumbai', 'mumbai', 'Maharashtra'),
            ('Delhi', 'delhi', 'Delhi'),
            ('Bangalore', 'bangalore', 'Karnataka'),
            ('Chennai', 'chennai', 'Tamil Nadu'),
            ('Hyderabad', 'hyderabad', 'Telangana'),
        ]
        cities = []
        for name, slug, state in cities_data:
            city, _ = City.objects.get_or_create(
                slug=slug, defaults={'name': name, 'state': state}
            )
            cities.append(city)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(cities)} cities created'))
        return cities

    def create_seat_categories(self):
        from apps.theaters.models import SeatCategory
        categories_data = [
            ('Silver', '#94a3b8', Decimal('1.0')),
            ('Gold', '#f59e0b', Decimal('1.5')),
            ('Platinum', '#818cf8', Decimal('2.0')),
        ]
        categories = []
        for name, color, multiplier in categories_data:
            cat, _ = SeatCategory.objects.get_or_create(
                name=name, defaults={'color_code': color, 'price_multiplier': multiplier}
            )
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(categories)} seat categories created'))
        return categories

    def create_theaters(self, cities):
        from apps.theaters.models import Theater
        theaters = []
        theater_names = [
            'CineMax Multiplex', 'PVR Cinemas', 'INOX Movies',
            'Raj Mandir', 'Galaxy Cinema',
        ]
        for i, city in enumerate(cities):
            for j, name in enumerate(theater_names[:2]):  # 2 theaters per city
                theater, _ = Theater.objects.get_or_create(
                    slug=f'{name.lower().replace(" ", "-")}-{city.slug}',
                    defaults={
                        'name': f'{name} - {city.name}',
                        'city': city,
                        'address': f'{random.randint(1, 500)} Main Street, {city.name}',
                        'phone': f'+91 98{random.randint(10000000, 99999999)}',
                        'email': f'info@{name.lower().replace(" ", "")}.{city.slug}.com',
                    }
                )
                theaters.append(theater)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(theaters)} theaters created'))
        return theaters

    def create_screens(self, theaters, categories):
        from apps.theaters.models import Screen, Seat
        screens = []
        screen_configs = [
            ('Screen 1', 'standard', 8, 12),   # 8 rows, 12 seats per row = 96 seats
            ('Screen 2', 'imax', 10, 16),       # 10 rows, 16 seats = 160 seats
        ]

        for theater in theaters:
            for screen_name, screen_type, rows, cols in screen_configs:
                total = rows * cols
                screen, created = Screen.objects.get_or_create(
                    theater=theater, name=screen_name,
                    defaults={'screen_type': screen_type, 'total_seats': total}
                )
                if created:
                    # Create seats
                    seats = []
                    row_labels = [chr(65 + r) for r in range(rows)]  # A, B, C, ...
                    for r, label in enumerate(row_labels):
                        # Assign category based on row position
                        if r < rows // 3:
                            cat = categories[0]  # Silver (front)
                        elif r < 2 * rows // 3:
                            cat = categories[1]  # Gold (middle)
                        else:
                            cat = categories[2]  # Platinum (back)
                        
                        for col in range(1, cols + 1):
                            seats.append(Seat(
                                screen=screen, category=cat,
                                row_label=label, seat_number=col,
                            ))
                    Seat.objects.bulk_create(seats)
                screens.append(screen)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(screens)} screens with seats created'))
        return screens

    def create_shows(self, movies, screens, categories):
        from apps.theaters.models import Show, ShowSeatPrice
        shows = []
        base_prices = {
            'Silver': Decimal('150'),
            'Gold': Decimal('250'),
            'Platinum': Decimal('400'),
        }

        # Create shows for the next 7 days
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        show_times = [
            (9, 30), (12, 30), (15, 30), (18, 30), (21, 30),
        ]

        for day_offset in range(7):
            show_date = today + timedelta(days=day_offset)
            for screen in screens:
                # Assign 2 different movies per screen per day
                screen_movies = random.sample(
                    [m for m in movies if m.release_date <= show_date.date()],
                    min(2, len([m for m in movies if m.release_date <= show_date.date()]))
                )
                for i, movie in enumerate(screen_movies):
                    # Pick show times for this movie
                    movie_times = show_times[i * 2:(i + 1) * 2 + 1]
                    for hour, minute in movie_times:
                        start = show_date.replace(hour=hour, minute=minute)
                        end = start + movie.duration

                        show, created = Show.objects.get_or_create(
                            screen=screen, start_time=start,
                            defaults={
                                'movie': movie,
                                'end_time': end,
                            }
                        )
                        if created:
                            # Set prices per category
                            for cat in categories:
                                price = base_prices.get(cat.name, Decimal('200'))
                                # Weekend surcharge
                                if show_date.weekday() >= 5:
                                    price = price * Decimal('1.2')
                                ShowSeatPrice.objects.get_or_create(
                                    show=show, category=cat,
                                    defaults={'price': price.quantize(Decimal('1'))}
                                )
                        shows.append(show)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(shows)} shows created'))
        return shows

    def create_sample_bookings(self, shows):
        from apps.bookings.models import Booking, BookedSeat
        from apps.theaters.models import Seat

        users = list(User.objects.filter(is_superuser=False)[:5])
        if not users:
            return

        booking_count = 0
        for i in range(20):
            user = random.choice(users)
            show = random.choice(shows[:len(shows) // 2])  # Past/current shows
            
            available_seats = list(
                Seat.objects.filter(screen=show.screen, is_active=True)
                .exclude(bookedseat__booking__show=show, bookedseat__booking__status='confirmed')
                [:random.randint(1, 4)]
            )

            if not available_seats:
                continue

            total = sum(
                show.seat_prices.filter(category=s.category).values_list('price', flat=True).first() or Decimal('200')
                for s in available_seats
            )

            booking = Booking.objects.create(
                user=user,
                show=show,
                total_amount=total,
                status='confirmed',
                booking_id=Booking.generate_booking_id(),
                confirmed_at=timezone.now() - timedelta(hours=random.randint(1, 72)),
            )

            for seat in available_seats:
                price = show.seat_prices.filter(category=seat.category).values_list('price', flat=True).first() or Decimal('200')
                BookedSeat.objects.create(booking=booking, seat=seat, price=price)

            booking_count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {booking_count} sample bookings created'))

    def create_bulk_bookings(self, shows, target_count):
        """Create bulk bookings for performance testing."""
        from apps.bookings.models import Booking, BookedSeat
        from apps.theaters.models import Seat

        users = list(User.objects.filter(is_superuser=False))
        if not users:
            return

        self.stdout.write(f'  ⏳ Creating {target_count} bookings (this may take a while)...')

        batch_size = 1000
        created = 0

        while created < target_count:
            bookings = []
            for _ in range(min(batch_size, target_count - created)):
                user = random.choice(users)
                show = random.choice(shows)
                days_ago = random.randint(0, 365)
                
                booking = Booking(
                    user=user,
                    show=show,
                    total_amount=Decimal(str(random.randint(150, 2000))),
                    status=random.choices(
                        ['confirmed', 'cancelled', 'refunded'],
                        weights=[85, 10, 5]
                    )[0],
                    booking_id=Booking.generate_booking_id(),
                    confirmed_at=timezone.now() - timedelta(days=days_ago),
                    created_at=timezone.now() - timedelta(days=days_ago),
                )
                bookings.append(booking)

            Booking.objects.bulk_create(bookings, ignore_conflicts=True)
            created += len(bookings)

            if created % 10000 == 0:
                self.stdout.write(f'    ... {created}/{target_count} bookings created')

        self.stdout.write(self.style.SUCCESS(f'  ✓ {created} bulk bookings created'))
