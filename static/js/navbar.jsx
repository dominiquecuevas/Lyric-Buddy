function NavBar(props) {
    return (
        <nav id="nav" className="navbar sticky-top navbar-light bg-light justify-content-start">
        <div id="note"><a className="navbar-brand" href="/"><span id="logo">♫</span> <b>Note</b>
            <br />
            <span id="slogan">Lyrics Annotator</span>
            </a>
        </div> | 
        {/* <a className="nav-link" onClick={props.handleAnnoSongs} href="/annosongs">Annotated Songs</a> | */}
        <Link className="nav-link" to="/annosongs">Annotated Songs</Link> |
        <a className="nav-link" onClick={props.handleUserAnnos} href="/user-annos">Account</a>
    </nav>
    )
}