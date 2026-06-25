(function () {
    'use strict';

    var fab = document.getElementById('help-chat-fab');
    var panel = document.getElementById('help-chat-panel');
    if (!fab || !panel) return;

    var messagesEl = panel.querySelector('.help-chat-messages');
    var form = panel.querySelector('.help-chat-form');
    var input = panel.querySelector('input[name="q"]');
    var sendBtn = panel.querySelector('.help-chat-send');
    var closeBtn = panel.querySelector('.help-chat-close');
    var chatUrl = panel.dataset.chatUrl;
    var suggestionsUrl = panel.dataset.suggestionsUrl;
    var booted = false;

    function esc(s) {
        return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function appendMsg(role, html) {
        var div = document.createElement('div');
        div.className = 'help-chat-msg ' + role;
        div.innerHTML = html;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function renderLinks(links) {
        if (!links || !links.length) return '';
        var html = '<div class="help-chat-links">';
        links.forEach(function (l) {
            html += '<a href="' + esc(l.url) + '">' + esc(l.source) + ': ' + esc(l.title) + '</a>';
        });
        html += '</div>';
        return html;
    }

    function renderSuggestions(items) {
        if (!items || !items.length) return '';
        var html = '<div class="help-chat-suggestions">';
        items.slice(0, 4).forEach(function (q) {
            html += '<button type="button" data-q="' + esc(q) + '">' + esc(q) + '</button>';
        });
        html += '</div>';
        return html;
    }

    function bindSuggestionClicks(root) {
        (root || messagesEl).querySelectorAll('.help-chat-suggestions button[data-q]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                ask(btn.getAttribute('data-q'));
            });
        });
    }

    function setOpen(open) {
        panel.classList.toggle('is-open', open);
        fab.classList.toggle('is-open', open);
        fab.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (open && !booted) {
            booted = true;
            loadSuggestions();
        }
        if (open) {
            setTimeout(function () { input.focus(); }, 120);
        }
    }

    function loadSuggestions() {
        fetch(suggestionsUrl, { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.ok) return;
                appendMsg('bot',
                    'Olá! Sou o assistente do SetSync. Pergunte sobre cifras, setlists, agenda, estúdios ou planos.' +
                    renderSuggestions(data.suggestions)
                );
                bindSuggestionClicks();
            })
            .catch(function () {
                appendMsg('bot', 'Olá! Pergunte sobre cifras, setlists, agenda, estúdios ou planos.');
            });
    }

    function ask(question) {
        var q = (question || '').trim();
        if (!q) return;
        appendMsg('user', esc(q));
        input.value = '';
        sendBtn.disabled = true;
        fetch(chatUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ q: q }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.ok) {
                    appendMsg('bot', esc(data.error || 'Não foi possível responder agora.'));
                    return;
                }
                var html = '';
                if (data.title) {
                    html += '<strong>' + esc(data.title) + '</strong><br>';
                }
                html += data.answer;
                html += renderLinks(data.links);
                if (data.ctas && data.ctas.length) {
                    html += '<div class="help-chat-links mt-2">';
                    data.ctas.forEach(function (c) {
                        html += '<a href="' + esc(c.url) + '" class="btn btn-sm btn-primary">' + esc(c.label) + '</a>';
                    });
                    html += '</div>';
                }
                appendMsg('bot', html);
                bindSuggestionClicks();
            })
            .catch(function () {
                appendMsg('bot', 'Erro de conexão. Tente de novo ou veja a <a href="/ajuda">Ajuda</a>.');
            })
            .finally(function () {
                sendBtn.disabled = false;
                input.focus();
            });
    }

    fab.addEventListener('click', function () {
        setOpen(!panel.classList.contains('is-open'));
    });
    closeBtn.addEventListener('click', function () {
        setOpen(false);
    });
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        ask(input.value);
    });
})();
