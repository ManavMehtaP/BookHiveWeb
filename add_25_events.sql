-- Add 25 events across all genres with uneven distribution
-- Distribution: Music(6), Festivals(5), Food & Drink(4), Sports(4), Art(3), Comedy(3)

-- MUSIC EVENTS (6 events)
INSERT INTO events (title, genre, location, venue, event_date, event_time, event_end_time, price, available_seats, total_seats, image_url, description, featured, status, created_by) VALUES
('Rock Concert 2026', 'Music', 'Madison Square Garden, New York', 'Main Arena', '2026-03-15', '20:00:00', '23:30:00', 125.00, 500, 800, 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800', 'An epic rock concert featuring top bands from around the world.', TRUE, 'active', 1),
('Jazz Night Live', 'Music', 'Blue Note, New York', 'Main Stage', '2026-04-02', '19:30:00', '22:00:00', 85.00, 150, 200, 'https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=800', 'Intimate jazz evening with renowned musicians.', FALSE, 'active', 1),
('Electronic Music Festival', 'Music', 'Brooklyn Warehouse, New York', 'Main Floor', '2026-05-20', '18:00:00', '02:00:00', 95.00, 1000, 1500, 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800', 'All-night electronic music festival with international DJs.', TRUE, 'active', 1),
('Classical Symphony', 'Music', 'Lincoln Center, New York', 'Philharmonic Hall', '2026-06-10', '19:00:00', '21:30:00', 150.00, 300, 400, 'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800', 'Classical music performance by the city philharmonic.', FALSE, 'active', 1),
('Indie Music Showcase', 'Music', 'Bowery Ballroom, New York', 'Main Stage', '2026-07-08', '20:00:00', '23:00:00', 45.00, 200, 250, 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800', 'Discover the best indie artists in an intimate setting.', FALSE, 'active', 1),
('Summer Pop Concert', 'Music', 'Central Park, New York', 'Outdoor Stage', '2026-08-12', '18:30:00', '22:00:00', 75.00, 2000, 3000, 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800', 'Free outdoor pop concert featuring chart-topping artists.', TRUE, 'active', 1),

-- FESTIVALS (5 events)
('Spring Cultural Festival', 'Festivals', 'Prospect Park, Brooklyn', 'Festival Grounds', '2026-03-25', '10:00:00', '20:00:00', 35.00, 1500, 2000, 'https://images.unsplash.com/photo-1531194066797-3a5601d5cd73?w=800', 'Celebrate spring with cultural performances, food, and art.', TRUE, 'active', 1),
('Food Truck Festival', 'Festivals', 'Hudson River Park, New York', 'Pier 86', '2026-04-15', '11:00:00', '22:00:00', 25.00, 800, 1000, 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800', 'Taste cuisines from 50+ food trucks in one location.', FALSE, 'active', 1),
('Renaissance Fair', 'Festivals', 'Forest Park, Queens', 'Fairgrounds', '2026-05-05', '10:00:00', '18:00:00', 40.00, 1200, 1500, 'https://images.unsplash.com/photo-1544966583-7c60d6851b0b?w=800', 'Step back in time with medieval games, crafts, and entertainment.', FALSE, 'active', 1),
('Film Festival Weekend', 'Festivals', 'Tribeca, New York', 'Multiple Venues', '2026-06-20', '12:00:00', '23:00:00', 55.00, 600, 800, 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=800', 'Three days of independent films, documentaries, and shorts.', TRUE, 'active', 1),
('Harvest Festival', 'Festivals', 'Queens County Farm, New York', 'Farm Grounds', '2026-09-30', '09:00:00', '17:00:00', 30.00, 2000, 2500, 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800', 'Fall celebration with pumpkin picking, hayrides, and local crafts.', FALSE, 'active', 1),

-- FOOD & DRINK (4 events)
('Wine Tasting Evening', 'Food & Drink', 'Manhattan Winery, New York', 'Tasting Room', '2026-03-18', '18:00:00', '21:00:00', 120.00, 80, 100, 'https://images.unsplash.com/photo-1566479179817-4a7a2a8e0b4c?w=800', 'Exclusive wine tasting with premium vintages and expert sommeliers.', FALSE, 'active', 1),
('Craft Beer Festival', 'Food & Drink', 'Brooklyn Brewery, New York', 'Main Hall', '2026-04-08', '14:00:00', '20:00:00', 65.00, 400, 500, 'https://images.unsplash.com/photo-1566479179817-4a7a2a8e0b4c?w=800', 'Sample 100+ craft beers from local and international breweries.', TRUE, 'active', 1),
('Chef Table Experience', 'Food & Drink', 'Michelin Star Restaurant, New York', 'Private Dining', '2026-05-12', '19:00:00', '22:30:00', 250.00, 20, 20, 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800', 'Intimate dining experience with a renowned Michelin-starred chef.', FALSE, 'active', 1),
('BBQ Championship', 'Food & Drink', 'Coney Island, Brooklyn', 'Outdoor Arena', '2026-07-22', '11:00:00', '19:00:00', 45.00, 1500, 2000, 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800', 'Watch top BBQ masters compete for the championship title.', FALSE, 'active', 1),

-- SPORTS (4 events)
('Basketball Championship', 'Sports', 'Barclays Center, Brooklyn', 'Main Court', '2026-03-22', '19:30:00', '22:00:00', 180.00, 800, 1000, 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800', 'Eastern Conference Finals - Game 7. Don\'t miss the action!', TRUE, 'active', 1),
('Marathon 2026', 'Sports', 'Central Park, New York', 'Start Line', '2026-04-18', '07:00:00', '14:00:00', 100.00, 5000, 8000, 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800', 'Annual NYC Marathon - 26.2 miles through the city streets.', FALSE, 'active', 1),
('Tennis Open', 'Sports', 'USTA Billie Jean King Center, New York', 'Arthur Ashe Stadium', '2026-06-15', '11:00:00', '19:00:00', 150.00, 1200, 1500, 'https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=800', 'US Open Qualifying Tournament - watch future stars emerge.', FALSE, 'active', 1),
('Soccer Derby', 'Sports', 'Red Bull Arena, New Jersey', 'Stadium', '2026-08-05', '20:00:00', '22:30:00', 85.00, 2000, 2500, 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=800', 'Intense local rivalry match in the MLS season.', TRUE, 'active', 1),

-- ART (3 events)
('Modern Art Exhibition', 'Art', 'MoMA, New York', 'Gallery 1', '2026-03-28', '10:00:00', '18:00:00', 55.00, 300, 400, 'https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=800', 'Contemporary art from emerging artists worldwide.', FALSE, 'active', 1),
('Photography Showcase', 'Art', 'Brooklyn Museum, New York', 'Exhibition Hall', '2026-05-30', '11:00:00', '17:00:00', 40.00, 200, 250, 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800', 'Award-winning photography from the past decade.', FALSE, 'active', 1),
('Sculpture Garden Opening', 'Art', 'Metropolitan Museum, New York', 'Sculpture Garden', '2026-07-15', '18:00:00', '21:00:00', 75.00, 150, 200, 'https://images.unsplash.com/photo-1578321272176-b7bbc0679853?w=800', 'Exclusive opening of new outdoor sculpture installations.', TRUE, 'active', 1),

-- COMEDY (3 events)
('Stand-up Comedy Night', 'Comedy', 'Comedy Cellar, New York', 'Main Stage', '2026-03-20', '20:00:00', '22:30:00', 60.00, 100, 120, 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800', 'Lineup of NYC\'s best comedians for one night only.', FALSE, 'active', 1),
('Improv Comedy Show', 'Comedy', 'Upright Citizens Brigade, New York', 'Theatre', '2026-04-25', '19:30:00', '21:30:00', 45.00, 80, 100, 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800', 'Spontaneous comedy with audience participation.', FALSE, 'active', 1),
('Comedy Festival Gala', 'Comedy', 'Beacon Theatre, New York', 'Main Hall', '2026-06-25', '20:00:00', '23:00:00', 95.00, 2000, 2800, 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800', 'Annual comedy festival featuring headliners from TV and film.', TRUE, 'active', 1);

-- Update available seats to be realistic (80-90% of total)
UPDATE events SET available_seats = FLOOR(total_seats * 0.85) WHERE id > 6;
