export function Nav() {
  const links = [
    ['/', 'Dashboard'], ['/chat', 'Atman Chat'], ['/library', 'Library'], ['/learn', 'Learn'], ['/model-lab', 'Model Lab'],
    ['/correctness', 'Correctness'], ['/canonical', 'Canonical DB'], ['/acquisition', 'Acquisition'], ['/content', 'Content Studio'],
    ['/publishing', 'Publishing'], ['/analytics', 'Analytics'], ['/qwen', 'Qwen Gateway'], ['/accounts', 'Accounts'], ['/eval', 'NyayaBench'], ['/ops', 'Ops']
  ];
  return <nav className="nav">{links.map(([href, label]) => <a key={href} href={href}>{label}</a>)}</nav>;
}
