/**
 * Autocomplete de endereço (Google Places) no cadastro de estúdio.
 * Preenche cidade, bairro e endereço; callback: SetSyncInitStudioAddress
 */
(function () {
    'use strict';

    function byId(id) {
        return document.getElementById(id);
    }

    function pickComponent(components, types) {
        if (!components || !components.length) return '';
        for (var i = 0; i < types.length; i++) {
            var want = types[i];
            for (var j = 0; j < components.length; j++) {
                var c = components[j];
                if (c.types && c.types.indexOf(want) >= 0) {
                    return c.long_name || c.short_name || '';
                }
            }
        }
        return '';
    }

    function setCoords(lat, lng, placeId) {
        var latEl = byId('endereco_lat');
        var lngEl = byId('endereco_lng');
        var pidEl = byId('endereco_place_id');
        if (latEl) latEl.value = lat != null ? String(lat) : '';
        if (lngEl) lngEl.value = lng != null ? String(lng) : '';
        if (pidEl) pidEl.value = placeId || '';
    }

    function fillFromPlace(place) {
        var comps = place.address_components || [];
        var cidade = pickComponent(comps, [
            'locality',
            'administrative_area_level_2',
        ]);
        var bairro = pickComponent(comps, [
            'sublocality_level_1',
            'sublocality',
            'neighborhood',
        ]);
        var route = pickComponent(comps, ['route']);
        var number = pickComponent(comps, ['street_number']);
        var endereco = route;
        if (route && number) {
            endereco = route + ', ' + number;
        } else if (!route && place.formatted_address) {
            endereco = place.formatted_address.split(',')[0];
        }

        var cidadeEl = byId('cidade');
        var bairroEl = byId('bairro');
        var enderecoEl = byId('endereco');
        if (cidadeEl && cidade) cidadeEl.value = cidade.slice(0, 80);
        if (bairroEl && bairro) bairroEl.value = bairro.slice(0, 80);
        if (enderecoEl && endereco) enderecoEl.value = endereco.slice(0, 200);

        var loc = place.geometry && place.geometry.location;
        if (loc) {
            setCoords(loc.lat(), loc.lng(), place.place_id || '');
        } else {
            setCoords('', '', place.place_id || '');
        }
    }

    window.SetSyncInitStudioAddress = function () {
        var input = byId('studio-address-search');
        if (!input || !window.google || !google.maps || !google.maps.places) {
            return;
        }

        var autocomplete = new google.maps.places.Autocomplete(input, {
            componentRestrictions: { country: 'br' },
            fields: [
                'address_components',
                'formatted_address',
                'geometry',
                'place_id',
                'name',
            ],
            types: ['establishment', 'geocode'],
        });

        autocomplete.addListener('place_changed', function () {
            var place = autocomplete.getPlace();
            if (!place) return;
            var label = place.formatted_address || place.name || input.value;
            if (label) {
                input.value = label.length > 300 ? label.slice(0, 300) : label;
            }
            fillFromPlace(place);
        });

        input.addEventListener('input', function () {
            if (!(input.value || '').trim()) {
                setCoords('', '', '');
            }
        });
    };

    if (window.google && window.google.maps && window.google.maps.places) {
        window.SetSyncInitStudioAddress();
    }
})();
