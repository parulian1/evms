# Event Management System

## Overview
API for managing technical events and conferences using Django and Django REST Framework. This API
allow handle technical conferences, managing everything from event creation to attendee
registration and session scheduling.

## Features (requested)
1. Event Management
- [ ] Create, read, update, and delete events
- [ ] Track event capacity and venue details
- [ ] Handle event metadata (dates, descriptions, etc.)
2. Session Management
- [ ] Schedule sessions within events
- [ ] Prevent scheduling conflicts within tracks (requirement) 
- [ ] Manage speakers and time slots (requirement)
3. Attendee Registration
- [ ] Handle attendee registration
- [ ] Enforce event capacity limits
- [ ] Prevent duplicate registrations
4. Track Management
- [ ] Organize sessions into tracks
- [ ] Track creation and management

## Idea based on assumption from techinasia - Features (The one i worked on)
1. Event Management
- [ ] Create, read, update, and delete events
- [ ] Track event capacity and venue details
- [ ] Handle event metadata (dates, descriptions, etc.)
- [ ] Handling track and speaker time to avoid conflict
2. Session Management
- [ ] Schedule sessions within events
- [ ] Allowing events to be bundled as one or separate session and attendee will purchase / register into this session 
3. Attendee Registration
- [ ] Handle attendee registration
- [ ] Enforce combined event capacity at session as limit 
- [ ] Prevent duplicate registrations
4. Track Management
- [ ] Organize sessions into tracks
- [ ] Track creation and management
5. User 
- [ ] Allowing admin / staff to do CRUD for Event - Session - Track
- [ ] Allowing to store speaker / attendee / user profile into one table profile. 
<br/> <br/> 
TODO : allowing attendee / user to see their purchased session with information of the event that was included