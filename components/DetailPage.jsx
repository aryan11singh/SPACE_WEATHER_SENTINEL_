import Script from "next/script";

export default function DetailPage({ title, meta, cards }) {
  return (
    <div className="detail-page">
      <div className="header">
        <a href="/">← Back to dashboard</a>
        <button className="toggle" id="themeToggle" type="button">Toggle theme</button>
      </div>
      <section className="hero">
        <div className="panel">
          <h1>{title}</h1>
          <p className="meta">{meta}</p>
          <div className="grid" style={{ marginTop: 16 }}>
            {cards.map((card) => (
              <div className="card" key={card.title}>
                <h3>{card.title}</h3>
                <img src={card.image} alt={card.alt} loading="lazy" />
              </div>
            ))}
          </div>
        </div>
      </section>
      <Script src="/detail.js" strategy="afterInteractive" />
    </div>
  );
}
