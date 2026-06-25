#!/usr/bin/env python3
"""Cria conta demo completa para screenshots / merchandising do SetSync."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

DEMO_USERNAME = 'showcase'
DEMO_PASSWORD = 'SetSyncShowcase2026!'
DEMO_EMAIL = 'showcase@setsync.com.br'
DEMO_DISPLAY = 'Ana Costa'

BAND_NAME = 'Maré Alta'
BAND_DESC = (
    'Covers de MPB e rock para bares, festivais e eventos corporativos. '
    'Fortaleza — CE · desde 2019.'
)

SETLIST_CORPORATIVO = 'Corporativo — Happy hour'
SETLIST_CORPORATIVO_DESC = 'Versão enxuta (~1h) para eventos empresariais e festas privadas.'

# Bar do Porto / Beira Mar — Fortaleza (mapa embutido na agenda)
MAP_LAT = -3.7186
MAP_LNG = -38.5424

MEMBERS = [
    ('lucas_showcase', 'lucas@setsync.com.br', 'Lucas Mendes', 'member'),
    ('bia_showcase', 'bia@setsync.com.br', 'Bia Alves', 'member'),
    ('raf_showcase', 'raf@setsync.com.br', 'Rafael Drum', 'member'),
]

VOCALISTS = ['Ana Costa', 'Lucas Mendes']

SETLIST_NAME = 'Sábado — Bar do Porto'
SETLIST_DESC = 'Set principal: 2h de show, mix MPB e clássicos internacionais.'

EVENT_SHOW_TITLE = 'Show — Bar do Porto'
EVENT_SHOW_LOCATION = 'Bar do Porto, Rua dos Navegantes — Fortaleza, CE'

EVENT_ENSAIO_TITLE = 'Ensaio geral — pré-show'
EVENT_ENSAIO_LOCATION = 'Estúdio Maré Alta — Cocó, Fortaleza'


def _chordsheet_payload(key: str, bpm: float, source: str) -> str:
    return json.dumps({
        'source': source.strip(),
        'meta': {'key': key, 'bpm': str(int(bpm)), 'time_signature': '4/4'},
    }, ensure_ascii=False)


def _songs():
    """Repertório genérico: MPB, rock e pop — serve para qualquer tipo de banda."""
    return [
        {
            'titulo': 'Evidências',
            'artista': 'Chitãozinho & Xororó',
            'tom': 'A',
            'bpm': 92,
            'conteudo': """{title: Evidências}
{artist: Chitãozinho & Xororó}
{key: A}
{tempo: 92}

{start_of_verse: Verso}
[A]Quando eu digo que deixei de [E]te amar
[F#m7]É porque eu te [D]amo
[A]Quando eu digo que não quero [E]mais você
[F#m7]É porque eu te [D]quero
{end_of_verse}

{start_of_chorus: Refrão}
[D]Eu tenho medo de te dar [A]liberdade
[E]Medo de você não me [F#m7]encontrar nunca mais
[D]Por isso eu finjo que [A]não te quero
[E]Mas é só [D]evidências
{end_of_chorus}""",
            'grade': _chordsheet_payload('A', 92, """: Verso
A E F#m7 D
= Refrão
D A E F#m7 D A E D"""),
        },
        {
            'titulo': 'Tempo Perdido',
            'artista': 'Legião Urbana',
            'tom': 'C',
            'bpm': 112,
            'conteudo': """{title: Tempo Perdido}
{artist: Legião Urbana}
{key: C}
{tempo: 112}

{start_of_verse: Verso}
[C]Todos os dias quando acordo
[Am]Não tenho mais o tempo que passou
[F]Mas tenho muita coisa ainda pra [G]fazer
[C]Eu vejo o tempo passar
[Am]Mas não consigo parar
[F]E o tempo não me deixa [G]envelhecer
{end_of_verse}

{start_of_chorus: Refrão}
[F]Eu preciso encontrar alguém que [G]me dê a mão
[Am]E me leve pra longe daqui
[F]Alguém que me faça [G]esquecer
[Am]Pelo menos por um [G]dia
{end_of_chorus}""",
            'grade': _chordsheet_payload('C', 112, """: Verso
C Am F G
= Refrão
F G Am F G Am G"""),
        },
        {
            'titulo': 'Wonderwall',
            'artista': 'Oasis',
            'tom': 'Em',
            'bpm': 87,
            'apple': 'https://music.apple.com/br/album/wonderwall/1440650788?i=1440650799',
            'conteudo': """{title: Wonderwall}
{artist: Oasis}
{key: Em}
{tempo: 87}

{start_of_verse: Verso}
[Em7]Today is gonna be the [G]day that they're gonna
[D]Throw it back to [A]you
[Em7]By now you should've [G]somehow realized what you
[D]Gotta [A]do
{end_of_verse}

{start_of_chorus: Refrão}
[C]Because maybe, [D]you're gonna be the one that
[Em]Saves me, and [G]after all
[C]You're my [D]wonderwall
{end_of_chorus}""",
        },
        {
            'titulo': 'Garota de Ipanema',
            'artista': 'Tom Jobim & Vinícius',
            'tom': 'F',
            'bpm': 118,
            'conteudo': """{title: Garota de Ipanema}
{artist: Tom Jobim & Vinícius de Moraes}
{key: F}
{tempo: 118}

{start_of_verse: Verso}
[Fmaj7]Olha que coisa mais [G7]linda, mais cheia de graça
[Gm7]É ela menina que [C7]vem e que passa
[Fmaj7]Num doce balanço a [G7]caminho do mar
{end_of_verse}

{start_of_chorus: Refrão}
[Fmaj7]Moça do corpo [G7]dourado do sol de Ipanema
[Gm7]O seu balançado é [C7]mais que um poema
[Fmaj7]É a coisa mais [Bb7]linda que [Fmaj7]eu já vi passar
{end_of_chorus}""",
        },
        {
            'titulo': 'Stand By Me',
            'artista': 'Ben E. King',
            'tom': 'A',
            'bpm': 118,
            'conteudo': """{title: Stand By Me}
{artist: Ben E. King}
{key: A}
{tempo: 118}

{start_of_verse: Verso}
[A]When the night has come, and the [F#m]land is dark
[D]And the moon is the only [E]light we'll see
[A]No I won't be afraid, no I [F#m]won't be afraid
[D]Just as long as you [E]stand by me
{end_of_verse}

{start_of_chorus: Refrão}
[A]Darling, darling stand by [F#m]me, oh stand by me
[D]Oh stand, stand by me, [E]stand by me
{end_of_chorus}""",
        },
        {
            'titulo': 'Só Hoje',
            'artista': 'Jota Quest',
            'tom': 'G',
            'bpm': 96,
            'conteudo': """{title: Só Hoje}
{artist: Jota Quest}
{key: G}
{tempo: 96}

{start_of_verse: Verso}
[G]Eu sei que não posso [Em]viver sem você
[C]E que não dá pra [D]esquecer
[G]Cada detalhe que [Em]ficou pra trás
[C]Cada momento que a [D]gente passou
{end_of_verse}

{start_of_chorus: Refrão}
[Em]Só hoje eu quero [C]ficar aqui
[G]Só hoje eu quero [D]te ouvir
[Em]Só hoje eu quero [C]acreditar
[G]Que ainda dá pra [D]recomeçar
{end_of_chorus}""",
        },
        {
            'titulo': 'Hotel California',
            'artista': 'Eagles',
            'tom': 'Bm',
            'bpm': 74,
            'conteudo': """{title: Hotel California}
{artist: Eagles}
{key: Bm}
{tempo: 74}

{start_of_verse: Verso}
[Bm]On a dark desert highway, [F#]cool wind in my hair
[A]Warm smell of colitas rising [E]up through the air
[G]Up ahead in the distance, [D]I saw a shimmering light
[Em]My head grew heavy and my [F#]sight grew dim
{end_of_verse}

{start_of_chorus: Refrão}
[G]Welcome to the Hotel [D]California
[Em]Such a lovely place, such a [F#]lovely face
[G]Plenty of room at the Hotel [D]California
[Em]Any time of year you can [F#]find it here
{end_of_chorus}""",
            'grade': _chordsheet_payload('Bm', 74, """: Verso
Bm F# A E G D Em F#
= Refrão
G D Em F#"""),
        },
        {
            'titulo': 'Valerie',
            'artista': 'Amy Winehouse / Mark Ronson',
            'tom': 'Eb',
            'bpm': 104,
            'conteudo': """{title: Valerie}
{artist: Amy Winehouse}
{key: Eb}
{tempo: 104}

{start_of_verse: Verso}
[Eb]Well sometimes I go out by myself
[Cm]And I look across the water
[Ab]And I think of all the things, what you're doing
[Bb]And in my head I paint a picture
{end_of_verse}

{start_of_chorus: Refrão}
[Eb]Valerie, [Cm]Valerie
[Ab]Valerie, [Bb]Valerie
[Eb]Why don't you come on over [Cm]here
[Ab]Stop making a fool out of [Bb]me
{end_of_chorus}""",
        },
    ]


def ensure_user(username: str, email: str, password: str, display_name: str) -> str:
    from db import create_user, get_user_by_username, update_user_display_name

    u = get_user_by_username(username)
    if u:
        if display_name and (u.get('display_name') or '') != display_name:
            update_user_display_name(u['id'], display_name)
        return u['id']
    uid = create_user(username, email, password, display_name=display_name)
    if not uid:
        raise RuntimeError(f'Não foi possível criar usuário {username}')
    return uid


def polish_user(user_id: str, *, display_name: str, phone: str | None = None) -> None:
    from db import dismiss_onboarding_checklist, touch_user_last_login, update_user_profile

    update_user_profile(
        user_id,
        display_name=display_name,
        phone=phone or '',
        whatsapp_notify=True,
        email_notify=True,
    )
    dismiss_onboarding_checklist(user_id)
    touch_user_last_login(user_id)


def create_prepared_cifra(band_id: str, song: dict) -> str:
    from blueprints.cifras import _prepare_conteudo_for_save
    from db import create_cifra, update_cifra_streaming

    conteudo, cifra_json = _prepare_conteudo_for_save(
        song['conteudo'],
        titulo=song['titulo'],
        artista=song['artista'],
        tom_original=song['tom'],
    )
    cid = create_cifra(
        song['titulo'],
        song['artista'],
        song['tom'],
        conteudo,
        band_id,
        cifra_json=cifra_json,
        grade_json=song.get('grade'),
        bpm=song.get('bpm'),
    )
    apple = song.get('apple')
    if apple:
        update_cifra_streaming(cid, apple)
    return cid


def install_band_logo(band_id: str, title: str) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return

    from band_logos import delete_band_logo_files, logo_dir
    from db import set_band_logo_filename

    delete_band_logo_files(band_id)
    w, h = 520, 180
    img = Image.new('RGBA', (w, h), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((12, 12, w - 12, h - 12), radius=28, fill=(42, 181, 160, 255))
    draw.rounded_rectangle((28, 28, w - 28, h - 28), radius=20, fill=(15, 23, 42, 255))
    try:
        from PIL import ImageFont
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 52)
        sub = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    except OSError:
        font = ImageFont.load_default()
        sub = font
    draw.text((48, 48), title, fill=(255, 255, 255, 255), font=font)
    draw.text((48, 118), 'covers · MPB · rock', fill=(148, 163, 184, 255), font=sub)
    filename = f'{band_id}.png'
    img.save(logo_dir() / filename, 'PNG')
    set_band_logo_filename(band_id, filename)


def cleanup_showcase_bands(owner_id: str) -> None:
    from db import delete_band, get_owned_bands

    for band in get_owned_bands(owner_id):
        name = (band.get('name') or '').strip()
        if name in (BAND_NAME, 'SetSync Showcase'):
            delete_band(band['id'])


def main() -> int:
    from db import (
        add_band_member,
        add_band_vocalist,
        create_band,
        update_assinatura,
        update_band,
        update_event_fees,
    )
    from models_agenda import (
        EVENT_ENSAIO,
        EVENT_SHOW,
        create_band_event,
        respond_event_assignment,
        set_event_assignments,
    )
    from models_band_team import create_lineup, ensure_default_band_roles
    from models_setlist import add_cifra_to_setlist, create_setlist, set_setlist_vocalist
    from setlist_public import set_setlist_public_share

    print('=== SetSync — demo merchandising (pronto para print) ===\n')

    owner_id = ensure_user(DEMO_USERNAME, DEMO_EMAIL, DEMO_PASSWORD, DEMO_DISPLAY)
    polish_user(owner_id, display_name=DEMO_DISPLAY, phone='85999887766')

    member_ids = []
    phones = ['85988776655', '85977665544', '85966554433']
    for i, (uname, email, display, role) in enumerate(MEMBERS):
        uid = ensure_user(uname, email, DEMO_PASSWORD, display)
        polish_user(uid, display_name=display, phone=phones[i % len(phones)])
        member_ids.append((uid, display, role))

    cleanup_showcase_bands(owner_id)

    band_id = create_band(BAND_NAME, BAND_DESC, owner_id)
    update_band(band_id, BAND_NAME, BAND_DESC)
    install_band_logo(band_id, BAND_NAME)
    ensure_default_band_roles(band_id)

    for uid, _display, role in member_ids:
        if uid != owner_id:
            add_band_member(band_id, uid, role)

    v_ana = add_band_vocalist(band_id, VOCALISTS[0], user_id=owner_id)
    v_lucas = add_band_vocalist(band_id, VOCALISTS[1])

    update_assinatura(band_id, plano='pro', status='ativa')

    songs = _songs()
    cifra_ids = [create_prepared_cifra(band_id, song) for song in songs]

    roles = ['Vocal', 'Guitarra', 'Baixo', 'Bateria']
    all_member_ids = [owner_id] + [m[0] for m in member_ids]
    create_lineup(
        band_id,
        'Formação show',
        [
            {'user_id': uid, 'role_label': roles[i % len(roles)]}
            for i, uid in enumerate(all_member_ids)
        ],
    )

    setlist_id = create_setlist(band_id, SETLIST_NAME, SETLIST_DESC)
    set_setlist_vocalist(setlist_id, v_ana)
    for i, cid in enumerate(cifra_ids):
        vocalist = v_lucas if i % 3 == 1 else v_ana
        add_cifra_to_setlist(setlist_id, cid, position=i + 1, vocalist_id=vocalist)

    share_token = set_setlist_public_share(setlist_id, True)

    corp_id = create_setlist(band_id, SETLIST_CORPORATIVO, SETLIST_CORPORATIVO_DESC)
    for i, cid in enumerate(cifra_ids[:5]):
        add_cifra_to_setlist(corp_id, cid, position=i + 1, vocalist_id=v_ana)

    now = datetime.now()
    days_to_sat = (5 - now.weekday()) % 7 or 7
    show_start = (now + timedelta(days=days_to_sat)).replace(
        hour=21, minute=0, second=0, microsecond=0,
    )
    ensaio_start = (show_start - timedelta(days=2)).replace(hour=20, minute=0)

    ensaio_id = create_band_event(
        band_id,
        title=EVENT_ENSAIO_TITLE,
        event_type=EVENT_ENSAIO,
        starts_at=ensaio_start.strftime('%Y-%m-%d %H:%M:%S'),
        ends_at=(ensaio_start + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
        location=EVENT_ENSAIO_LOCATION,
        location_lat=MAP_LAT,
        location_lng=MAP_LNG,
        notes='Checklist: passagem de som, ordem do set, volumes de monitor.',
        setlist_id=setlist_id,
        created_by=owner_id,
    )

    show_id = create_band_event(
        band_id,
        title=EVENT_SHOW_TITLE,
        event_type=EVENT_SHOW,
        starts_at=show_start.strftime('%Y-%m-%d %H:%M:%S'),
        ends_at=(show_start + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
        location=EVENT_SHOW_LOCATION,
        location_lat=MAP_LAT,
        location_lng=MAP_LNG,
        notes='Entrada gratuita até 22h · repetição do set corporativo sob encomenda.',
        setlist_id=setlist_id,
        created_by=owner_id,
    )

    assignments = [
        {'user_id': uid, 'role_label': roles[i % len(roles)]}
        for i, uid in enumerate(all_member_ids)
    ]
    for event_id in (ensaio_id, show_id):
        set_event_assignments(event_id, assignments, assigned_by=owner_id)
        for uid in all_member_ids:
            respond_event_assignment(event_id, uid, accepted=True)

    update_event_fees(
        show_id,
        fee_total=1800.0,
        fee_transport_discount=150.0,
        fee_equipment_discount=80.0,
        fee_notes='Van rateada entre 4 músicos · equipamento do bar incluso.',
        fee_settled=False,
    )

    base = (os.getenv('SETSYNC_CANONICAL_URL') or 'https://setsync.com.br').rstrip('/')

    print('── Login ──')
    print(f'  Usuário:  {DEMO_USERNAME}')
    print(f'  E-mail:   {DEMO_EMAIL}')
    print(f'  Senha:    {DEMO_PASSWORD}')
    print(f'  Perfil:   {DEMO_DISPLAY} · WhatsApp cadastrado\n')

    print('── Banda ──')
    print(f'  {BAND_NAME} · plano Pro · logo · 8 cifras · 2 setlists · formação salva\n')

    print('── Telas para print ──')
    print(f'  Login:       {base}/auth/login')
    print(f'  Dashboard:   {base}/dashboard')
    print(f'  Banda:       {base}/bands/{band_id}')
    print(f'  Setlist:     {base}/setlists/{setlist_id}')
    print(f'  Corporativo: {base}/setlists/{corp_id}')
    print(f'  Modo Tocar:  {base}/setlists/{setlist_id}/tocar')
    print(f'  Ensaio:      {base}/agenda/{ensaio_id}')
    print(f'  Show+cachê:  {base}/agenda/{show_id}')
    if share_token:
        print(f'  Link público: {base}/setlists/letras/{share_token}')
    print()
    print('Conta pronta — entre com showcase e capture as telas.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
