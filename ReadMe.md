# Multi-Sector Implementation Guide

## 🎯 Overview

This API is **sector-agnostic** by design. The same codebase handles:
- Medical clinics (appointments, consultations)
- Real estate (property viewings, inspections)
- Taxi/Transportation (ride bookings, reservations)
- Laboratories (test bookings, sample collection)
- Hotels (room reservations, check-ins)
- Salons/Spas (styling appointments, treatments)
- Automotive (service appointments, repairs)
- Legal offices (consultations, meetings)
- Education (tutoring sessions, classes)
- **Any business with front desk operations**

## 🏗️ How It Works

### Core Design Principle

The database uses **flexible, generic fields** that work across all sectors:

```python
# Provider model - works for ANY business
class Provider(Base):
    name = "City Medical Clinic"        # OR "Downtown Apartments" OR "Quick Taxi"
    sector = "medical"                  # OR "real_estate" OR "transportation"
    phone = "+1234567890"
    email = "contact@business.com"
    address = "123 Main St"

# Booking model - works for ANY appointment type
class Booking(Base):
    provider_id = 1
    client_name = "John Doe"
    client_phone = "+1234567890"
    service_type = "consultation"       # OR "viewing" OR "ride" OR "test"
    scheduled_at = "2025-01-15T10:00:00"
    status = "pending"                  # Universal workflow
    notes = "Additional details"
```

### Why This Works

1. **Generic field names**: `service_type` instead of `appointment_type` or `booking_type`
2. **Flexible sector field**: Filter providers by industry
3. **Universal status flow**: pending → confirmed → completed
4. **Notes field**: Capture sector-specific details

## 📋 Sector Examples

### 1. Medical Clinics

```bash
# Create medical provider
curl -X POST "http://localhost:8000/providers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Medical Clinic",
    "sector": "medical",
    "phone": "+1234567890",
    "email": "info@citymedical.com",
    "address": "123 Health St"
  }'

# Book appointment
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 1,
    "client_name": "John Doe",
    "client_phone": "+1234567890",
    "service_type": "general_consultation",
    "scheduled_at": "2025-01-15T10:00:00",
    "notes": "First visit, bring medical history"
  }'

# Common service_types for medical:
# - general_consultation
# - specialist_consultation
# - follow_up
# - vaccination
# - lab_test_referral
# - emergency
```

### 2. Real Estate

```bash
# Create real estate provider
curl -X POST "http://localhost:8000/providers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Realty Group",
    "sector": "real_estate",
    "phone": "+1234567890",
    "email": "info@downtownrealty.com",
    "address": "456 Property Ave"
  }'

# Book property viewing
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 2,
    "client_name": "Jane Smith",
    "client_phone": "+1987654321",
    "service_type": "property_viewing",
    "scheduled_at": "2025-01-16T14:00:00",
    "notes": "Interested in 2BR apartment, budget $2000/month"
  }'

# Common service_types for real_estate:
# - property_viewing
# - home_inspection
# - appraisal_meeting
# - lease_signing
# - property_consultation
```

### 3. Taxi/Transportation

```bash
# Create taxi provider
curl -X POST "http://localhost:8000/providers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quick Taxi Services",
    "sector": "transportation",
    "phone": "+1234567890",
    "email": "dispatch@quicktaxi.com",
    "address": "789 Transport Blvd"
  }'

# Book ride
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 3,
    "client_name": "Mike Johnson",
    "client_phone": "+1555666777",
    "service_type": "airport_transfer",
    "scheduled_at": "2025-01-17T06:00:00",
    "notes": "Pickup: 123 Main St, Dropoff: City Airport Terminal 2"
  }'

# Common service_types for transportation:
# - airport_transfer
# - city_ride
# - hourly_rental
# - intercity_trip
# - corporate_transport
```

### 4. Laboratories

```bash
# Create laboratory provider
curl -X POST "http://localhost:8000/providers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Diagnostic Labs",
    "sector": "laboratory",
    "phone": "+1234567890",
    "email": "info@citydiagnostics.com",
    "address": "321 Science Park"
  }'

# Book test
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 4,
    "client_name": "Sarah Williams",
    "client_phone": "+1888999000",
    "service_type": "blood_test",
    "scheduled_at": "2025-01-18T08:00:00",
    "notes": "Fasting required. Test: Complete Blood Count (CBC)"
  }'

# Common service_types for laboratory:
# - blood_test
# - urine_test
# - x_ray
# - mri_scan
# - ct_scan
# - ultrasound
# - sample_collection
```

### 5. Hotels

```bash
# Create hotel provider
curl -X POST "http://localhost:8000/providers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grand Plaza Hotel",
    "sector": "hospitality",
    "phone": "+1234567890",
    "email": "reservations@grandplaza.com",
    "address": "555 Luxury Lane"
  }'

# Book room
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 5,
    "client_name": "David Lee",
    "client_phone": "+1222333444",
    "service_type": "room_reservation",
    "scheduled_at": "2025-01-20T15:00:00",
    "notes": "Check-in: Jan 20, Check-out: Jan 23. Deluxe room, 2 guests"
  }'

# Common service_types for hospitality:
# - room_reservation
# - event_booking
# - conference_room
# - spa_appointment
# - restaurant_reservation
```

### 6. Automotive/Garages

```bash
# Create automotive provider
curl -X POST "http://localhost:8000/providers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Expert Auto Repair",
    "sector": "automotive",
    "phone": "+1234567890",
    "email": "service@expertauto.com",
    "address": "777 Mechanic St"
  }'

# Book service
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 6,
    "client_name": "Tom Brown",
    "client_phone": "+1444555666",
    "service_type": "oil_change",
    "scheduled_at": "2025-01-19T09:00:00",
    "notes": "Vehicle: 2020 Honda Civic. Also check brake pads"
  }'

# Common service_types for automotive:
# - oil_change
# - tire_rotation
# - brake_service
# - engine_diagnostic
# - general_inspection
# - body_repair
```

### 7. Salons/Spas

```bash
# Create salon provider
curl -X POST "http://localhost:8000/providers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Elegant Beauty Salon",
    "sector": "beauty",
    "phone": "+1234567890",
    "email": "bookings@elegantbeauty.com",
    "address": "999 Style Avenue"
  }'

# Book appointment
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 7,
    "client_name": "Lisa Anderson",
    "client_phone": "+1777888999",
    "service_type": "haircut_coloring",
    "scheduled_at": "2025-01-21T11:00:00",
    "notes": "Full highlights and trim. Stylist preference: Maria"
  }'

# Common service_types for beauty:
# - haircut
# - haircut_coloring
# - manicure
# - pedicure
# - facial
# - massage
# - spa_package
```

## 🔍 Filtering by Sector

### Get all medical providers
```bash
curl "http://localhost:8000/providers/?sector=medical"
```

### Get all real estate agencies
```bash
curl "http://localhost:8000/providers/?sector=real_estate"
```

### Get all transportation providers
```bash
curl "http://localhost:8000/providers/?sector=transportation"
```

### Get bookings for specific sector
```bash
# First get provider IDs for sector
curl "http://localhost:8000/providers/?sector=laboratory"

# Then filter bookings by those providers
curl "http://localhost:8000/bookings/?provider_id=4"
```

## 🎨 Frontend Implementation

### Sector-Specific UI

Your frontend (React Native/Web) can customize UI based on sector:

```javascript
// Example React Native component
function BookingForm({ provider }) {
  const getServiceTypeLabel = () => {
    const labels = {
      medical: "Appointment Type",
      real_estate: "Service Type",
      transportation: "Trip Type",
      laboratory: "Test Type",
      hospitality: "Reservation Type",
      automotive: "Service Type",
      beauty: "Treatment Type"
    };
    return labels[provider.sector] || "Service Type";
  };

  const getServiceOptions = () => {
    const options = {
      medical: ["Consultation", "Follow-up", "Vaccination"],
      real_estate: ["Property Viewing", "Inspection", "Consultation"],
      transportation: ["City Ride", "Airport Transfer", "Hourly Rental"],
      laboratory: ["Blood Test", "X-Ray", "MRI Scan"],
      hospitality: ["Room Reservation", "Event Booking"],
      automotive: ["Oil Change", "Brake Service", "Inspection"],
      beauty: ["Haircut", "Manicure", "Facial"]
    };
    return options[provider.sector] || [];
  };

  return (
    <View>
      <Text>{getServiceTypeLabel()}</Text>
      <Picker>
        {getServiceOptions().map(option => (
          <Picker.Item key={option} label={option} value={option} />
        ))}
      </Picker>
    </View>
  );
}
```

## 📊 Recommended Sector Values

Use these standardized sector values for consistency:

```python
SUPPORTED_SECTORS = [
    "medical",           # Clinics, hospitals, doctors
    "dental",            # Dental clinics
    "real_estate",       # Property rentals, sales
    "transportation",    # Taxis, car rentals, shuttles
    "laboratory",        # Diagnostic labs, testing centers
    "hospitality",       # Hotels, resorts, lodges
    "automotive",        # Garages, repair shops
    "beauty",            # Salons, spas, barbershops
    "legal",             # Law firms, attorneys
    "education",         # Tutoring, training centers
    "veterinary",        # Pet clinics
    "fitness",           # Gyms, personal trainers
    "photography",       # Photo studios
    "consulting",        # Business consultants
    "maintenance",       # Home repairs, plumbing
    "food_service",      # Restaurants, catering
    "entertainment",     # Event venues, studios
    "other"              # Catch-all for new sectors
]
```

## 🚀 Advanced: Sector-Specific Validation

If you need sector-specific business rules, add them to the service layer:

```python
# In booking_service.py

class BookingService:
    def create_booking(self, data: BookingCreate):
        provider = self.provider_repo.get_by_id(data.provider_id)
        
        # Basic validation (all sectors)
        if not provider:
            raise ValueError("Provider not found")
        if data.scheduled_at < datetime.utcnow():
            raise ValueError("Cannot book in the past")
        
        # Sector-specific validation
        if provider.sector == "laboratory":
            # Labs only open 8 AM - 6 PM
            hour = data.scheduled_at.hour
            if hour < 8 or hour >= 18:
                raise ValueError("Laboratory bookings only available 8 AM - 6 PM")
        
        if provider.sector == "transportation":
            # Require pickup/dropoff in notes
            if not data.notes or "pickup" not in data.notes.lower():
                raise ValueError("Transportation bookings must include pickup location")
        
        if provider.sector == "hospitality":
            # Hotels require check-in/check-out dates
            if not data.notes or "check-out" not in data.notes.lower():
                raise ValueError("Hotel bookings must include check-out date")
        
        return self.booking_repo.create(data)
```

## 📈 Analytics by Sector

Query bookings by sector for analytics:

```python
# Example: Get booking counts by sector
from sqlalchemy import func

def get_bookings_by_sector(db: Session):
    result = db.query(
        Provider.sector,
        func.count(Booking.id).label('booking_count')
    ).join(
        Booking, Provider.id == Booking.provider_id
    ).group_by(
        Provider.sector
    ).all()
    
    return {sector: count for sector, count in result}

# Returns: {'medical': 45, 'real_estate': 23, 'transportation': 67}
```

## 🔧 Future Expansion

### Adding Sector-Specific Fields

If you need sector-specific data, add optional JSON fields:

```python
# In models/provider.py
from sqlalchemy.dialects.postgresql import JSON

class Provider(Base):
    # ... existing fields ...
    
    # Sector-specific metadata
    metadata = Column(JSON, nullable=True)
    
# Usage examples:
# Medical: {"specializations": ["cardiology", "pediatrics"], "insurance_accepted": ["Blue Cross", "Aetna"]}
# Real Estate: {"property_types": ["apartment", "house"], "price_range": "1000-3000"}
# Transportation: {"vehicle_types": ["sedan", "suv"], "max_passengers": 4}
# Laboratory: {"tests_offered": ["blood", "urine", "xray"], "fasting_required": true}
```

### Adding Service Catalog Table

For more structure, create a services table:

```python
class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    name = Column(String(255), nullable=False)  # "Blood Test", "Property Viewing"
    duration_minutes = Column(Integer)  # 30, 60, 90
    price = Column(Numeric(10, 2))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
```

Then bookings can reference specific services instead of freeform `service_type`.

## ✅ Summary

The current implementation is **100% multi-sector ready**:

1. ✅ **Generic data model** works for all sectors
2. ✅ **Sector field** for filtering and categorization
3. ✅ **Flexible service_type** field for any service
4. ✅ **Universal booking workflow** (pending → confirmed → completed)
5. ✅ **Notes field** captures sector-specific details
6. ✅ **No code changes needed** to add new sectors
7. ✅ **Frontend can customize** UI per sector
8. ✅ **Analytics possible** across all sectors

Just change the `sector` value when creating providers, and the system adapts automatically!