/**
 * Autocomplete de local (Google Places) no formulário da agenda.
 * Requer Maps JS API + Places; callback: SetSyncInitAgendaLocation
 */
(function () {
    'use strict';

    function byId(id) {
        return document.getElementById(id);
    }

    function setCoords(lat, lng, placeId) {
        var latEl = byId('location_lat');
        var lngEl = byId('location_lng');
        var pidEl = byId('location_place_id');
        if (latEl) latEl.value = lat != null ? String(lat) : '';
        if (lngEl) lngEl.value = lng != null ? String(lng) : '';
        if (pidEl) pidEl.value = placeId || '';
    }

    function bindManualClear(input) {
        input.addEventListener('input', function () {
            if (!(input.value || '').trim()) {
                setCoords('', '', '');
            }
        });
    }

    window.SetSyncInitAgendaLocation = function () {
        var input = byId('location');
        if (!input || !window.google || !google.maps || !google.maps.places) {
            return;
        }

        var autocomplete = new google.maps.places.Autocomplete(input, {
            componentRestrictions: { country: 'br' },
            fields: ['formatted_address', 'geometry', 'place_id', 'name'],
            types: ['establishment', 'geocode'],
        });

        autocomplete.addListener('place_changed', function () {
            var place = autocomplete.getPlace();
            if (!place) return;

            var label = place.formatted_address || place.name || input.value;
            if (label) {
                input.value = label.length > 300 ? label.slice(0, 300) : label;
            }

            var loc = place.geometry && place.geometry.location;
            if (loc) {
                setCoords(loc.lat(), loc.lng(), place.place_id || '');
            } else {
                setCoords('', '', place.place_id || '');
            }
        });

        bindManualClear(input);
    };

    if (window.google && window.google.maps && window.google.maps.places) {
        window.SetSyncInitAgendaLocation();
    }
})();
