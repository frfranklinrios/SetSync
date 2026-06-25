/**
 * IndexedDB — pacotes offline por banda.
 */
(function (global) {
  'use strict';

  var DB_NAME = 'setsync-offline';
  var DB_VERSION = 1;
  var STORE = 'packs';

  function openDb() {
    return new Promise(function (resolve, reject) {
      var req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onerror = function () { reject(req.error); };
      req.onupgradeneeded = function () {
        var db = req.result;
        if (!db.objectStoreNames.contains(STORE)) {
          db.createObjectStore(STORE, { keyPath: 'band_id' });
        }
      };
      req.onsuccess = function () { resolve(req.result); };
    });
  }

  function withStore(mode, fn) {
    return openDb().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(STORE, mode);
        var store = tx.objectStore(STORE);
        Promise.resolve(fn(store))
          .then(function (val) {
            tx.oncomplete = function () { resolve(val); };
            tx.onerror = function () { reject(tx.error); };
          })
          .catch(reject);
      });
    });
  }

  function reqToPromise(req) {
    return new Promise(function (resolve, reject) {
      req.onsuccess = function () { resolve(req.result); };
      req.onerror = function () { reject(req.error); };
    });
  }

  function savePack(bandId, pack) {
    return withStore('readwrite', function (store) {
      return reqToPromise(store.put(pack));
    });
  }

  function getPack(bandId) {
    return withStore('readonly', function (store) {
      return reqToPromise(store.get(String(bandId)));
    });
  }

  function listPacks() {
    return withStore('readonly', function (store) {
      return reqToPromise(store.getAll());
    });
  }

  function deletePack(bandId) {
    return withStore('readwrite', function (store) {
      return reqToPromise(store.delete(String(bandId)));
    });
  }

  global.SetSyncOfflineStore = {
    savePack: savePack,
    getPack: getPack,
    listPacks: listPacks,
    deletePack: deletePack,
    isSupported: function () { return !!global.indexedDB; },
  };
})(window);
