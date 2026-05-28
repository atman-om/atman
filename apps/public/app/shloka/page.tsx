export default function ShlokaPage() {
  return (
    <div className="card">
      <h2>Shloka Explainer</h2>
      <p>
        v0.6 placeholder flow: enter a canonical locator such as BG.2.47 after corpus seeding.
        Production behavior must verify Sanskrit text against source corpus before explanation.
      </p>
      <input placeholder="BG.2.47" />
      <p><button disabled>Explain after source-locator endpoint ships</button></p>
    </div>
  );
}
