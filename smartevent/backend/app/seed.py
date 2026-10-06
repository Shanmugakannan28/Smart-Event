from datetime import timedelta
from .database import utcnow
from .models import Event

# title, category, location, days from now, price (INR), tickets, description, banner file
SAMPLES = [
    ("Sunset Beats Festival", "Music", "Hyderabad, HITEX Grounds", 12, 1499, 300,
     "An open-air evening of indie and electronic acts as the sun goes down. Food trucks, art installations and a main stage with a full light show.", "sunset-beats.svg"),
    ("React & FastAPI Summit", "Tech", "Bengaluru, Tech Park Hall A", 20, 999, 150,
     "A full day of talks and hands-on workshops on building modern full-stack apps, from API design to production deployment.", "tech-summit.svg"),
    ("City Marathon 10K", "Sports", "Chennai, Marina Beach", 30, 499, 500,
     "A scenic community 10K along the coast with timing chips, hydration points, finisher medals and a post-race breakfast.", "city-marathon.svg"),
    ("Startup Founders Meetup", "Business", "Mumbai, BKC Convention Centre", 8, 799, 120,
     "Pitch sessions, investor panels and structured networking for early-stage founders and the people who back them.", "founders-meetup.svg"),
    ("Acoustic Nights", "Music", "Pune, Blue Frog Studio", 5, 599, 80,
     "An intimate evening of unplugged live sets from local singer-songwriters, in a small room with great sound.", "acoustic-nights.svg"),
    ("AI Builders Hackathon", "Tech", "Hyderabad, T-Hub", 15, 299, 200,
     "Twenty-four hours to build something with machine learning. Mentors on site, cloud credits for every team, prizes for the best demos.", "ai-hackathon.svg"),
    ("Inter-College Football Cup", "Sports", "Delhi, Jawaharlal Nehru Stadium", 25, 349, 400,
     "Quarter-finals of the annual university tournament. Floodlit match, live commentary and food stalls around the ground.", "football-cup.svg"),
    ("Leadership Forum 2026", "Business", "Kolkata, Taj Bengal", 40, 2499, 100,
     "A one-day forum for product and engineering leaders: keynotes, small-group roundtables and a closing dinner.", "leadership-forum.svg"),
]


def seed_events(db):
    if db.query(Event).count():
        # Upgrade older databases that still use placeholder photos.
        for title, *_rest, banner in SAMPLES:
            ev = db.query(Event).filter(Event.title == title, Event.banner_image.like("%picsum.photos%")).first()
            if ev:
                ev.banner_image = f"/static/banners/{banner}"
        db.commit()
        return
    for title, cat, loc, days, price, qty, desc, banner in SAMPLES:
        db.add(Event(title=title, category=cat, location=loc, description=desc,
                     event_date=(utcnow() + timedelta(days=days)).replace(hour=18, minute=0, second=0, microsecond=0),
                     ticket_price=price, total_tickets=qty, available_tickets=qty,
                     banner_image=f"/static/banners/{banner}"))
    db.commit()
