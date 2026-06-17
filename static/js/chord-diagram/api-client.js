/** Cliente da API musical v1 — integração com o modal de diagramas */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  function apiBase() {
    return '/api/v1';
  }

  function normalizeFrets(frets) {
    return (frets || []).map(function (f) {
      if (f === 'X' || f === 'x') return 'x';
      return f;
    });
  }

  CD.positionsToShapeOptions = function positionsToShapeOptions(positions) {
    return (positions || []).map(function (p, idx) {
      return {
        frets: normalizeFrets(p.frets),
        fingers: p.fingers || null,
        label: p.label || ('Posição ' + (idx + 1)),
        source: p.source || 'API',
        positionId: p.positionId,
        baseFret: p.baseFret,
        barres: p.barres || [],
      };
    });
  };

  CD.fetchModalChords = function fetchModalChords(symbol, instrument) {
    var url = apiBase() + '/chords?symbol=' + encodeURIComponent(symbol) +
      '&instrument=' + encodeURIComponent(instrument || 'violao') +
      '&format=modal';
    return fetch(url, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    }).then(function (r) {
      return r.json().then(function (data) {
        if (!r.ok) throw new Error((data && data.error) || 'Erro na API');
        return data;
      });
    });
  };

  CD.fetchScaleMap = function fetchScaleMap(root, scaleType, instrument) {
    var url = apiBase() + '/scales?root=' + encodeURIComponent(root) +
      '&type=' + encodeURIComponent(scaleType) +
      '&instrument=' + encodeURIComponent(instrument || 'violao');
    return fetch(url, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    }).then(function (r) { return r.json(); });
  };

  CD.fetchVextab = function fetchVextab(symbol, instrument, pos) {
    var url = apiBase() + '/notation/vexflow?symbol=' + encodeURIComponent(symbol) +
      '&instrument=' + encodeURIComponent(instrument || 'violao') +
      '&pos=' + (pos || 0);
    return fetch(url, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    }).then(function (r) { return r.json(); });
  };

  CD.fetchArpeggio = function fetchArpeggio(symbol, instrument, pattern) {
    var url = apiBase() + '/arpeggios?symbol=' + encodeURIComponent(symbol) +
      '&instrument=' + encodeURIComponent(instrument || 'baixo') +
      '&pattern=' + encodeURIComponent(pattern || 'root');
    return fetch(url, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    }).then(function (r) { return r.json(); });
  };

  CD.renderServerSvg = function renderServerSvg(symbol, instrument, pos) {
    var url = apiBase() + '/render/fretboard?symbol=' + encodeURIComponent(symbol) +
      '&instrument=' + encodeURIComponent(instrument || 'violao') +
      '&pos=' + (pos || 0);
    return url;
  };
})(typeof window !== 'undefined' ? window : globalThis);
