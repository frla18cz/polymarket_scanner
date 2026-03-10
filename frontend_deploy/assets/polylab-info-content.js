(function () {
  window.POLYLAB_INFO_CONTENT = Object.freeze({
    contactEmail: 'hello@polylab.app',
    contact: {
      email: 'hello@polylab.app'
    },
    customData: {
      navLabel: 'Custom Data',
      teaser: {
        eyebrow: 'For funds, desks, and analysts',
        title: 'Need custom Polymarket data for a team?',
        body: 'PolyLab can package enriched market snapshots, holder data, and smart-money context as bespoke exports or private feeds.',
        ctaLabel: 'Explore Custom Data',
        href: '/custom-data',
        pointOne: 'Bespoke exports built around your market universe or tag set.',
        pointTwo: 'Private API-style delivery for internal dashboards and research workflows.',
        pointThree: 'Holder and smart-money enrichment on top of raw Polymarket market data.'
      },
      landingCallout: {
        title: 'Need a private feed instead of the public app?',
        body: 'Ask about custom Polymarket data delivery for research teams, builders, or internal dashboards.',
        ctaLabel: 'Custom Data',
        href: '/custom-data'
      },
      page: {
        heroEyebrow: 'Custom Data',
        heroTitle: 'Custom Polymarket data for research teams',
        heroBody: 'Get enriched market snapshots, holder data, and smart-money context delivered in the format your team actually works with.',
        heroNote: 'Private API access and bespoke exports for funds, research desks, and builders.',
        proofOneTitle: 'Built on the same market layer as PolyLab',
        proofOneBody: 'Market snapshots already include price, spread, APR, liquidity, volume, expiry, and tag context.',
        proofTwoTitle: 'Holder and smart-money enrichment',
        proofTwoBody: 'Pair raw markets with holder counts, profitable-versus-losing positioning, and market-level context.',
        proofThreeTitle: 'Independent Polymarket analysis layer',
        proofThreeBody: 'Useful when your team wants a clean input layer without rebuilding the enrichment workflow from scratch.',
        capabilityOneTitle: 'Latest market snapshot feeds',
        capabilityOneBody: 'Get current market snapshots with probability, spread, APR, liquidity, volume, expiry, and category context in one schema.',
        capabilityTwoTitle: 'Holder and smart-money enrichment',
        capabilityTwoBody: 'Add top-holder coverage, profitable-versus-losing wallet context, and market-level smart-money signals where relevant.',
        capabilityThreeTitle: 'Tailored market universes',
        capabilityThreeBody: 'Scope delivery around specific tags, event clusters, market filters, or internal watchlists instead of one generic dump.',
        deliveryOneTitle: 'Private API access',
        deliveryOneBody: 'Expose the data through a lightweight private feed for internal dashboards, research notebooks, or downstream services.',
        deliveryTwoTitle: 'Scheduled JSON or CSV exports',
        deliveryTwoBody: 'Get recurring deliveries in the format your team already uses when a full API integration is unnecessary.',
        deliveryThreeTitle: 'Bespoke schemas and field selection',
        deliveryThreeBody: 'Keep only the fields your team cares about and shape the payload around the workflow instead of the raw source format.',
        audienceOneTitle: 'Funds and research desks',
        audienceOneBody: 'Use PolyLab as a faster input layer for market scouting, thematic monitoring, and internal analyst workflows.',
        audienceTwoTitle: 'Media and newsletter teams',
        audienceTwoBody: 'Pull cleaner market datasets for coverage, rankings, and recurring prediction-market analysis without manual extraction.',
        audienceThreeTitle: 'Builders and product teams',
        audienceThreeBody: 'Use custom feeds as a shortcut when you need enriched Polymarket data inside a product, internal tool, or client workflow.',
        ctaTitle: 'Tell me what your team needs',
        ctaBody: 'If you need a private feed, recurring export, or custom schema, reach out and I can scope it directly with you.',
        ctaLabel: 'Request Custom Data',
        ctaHref: 'mailto:hello@polylab.app?subject=Custom%20Data%20Inquiry',
        faq: [
          {
            question: 'What kind of data can PolyLab deliver?',
            answer: 'PolyLab can deliver current market snapshots, derived fields such as APR and spread, tag-filtered market sets, and holder or smart-money enrichment where available.'
          },
          {
            question: 'Is this a public self-serve API?',
            answer: 'Not in this version. The initial offer is private and bespoke, scoped around the needs of a specific team rather than exposed as a public self-serve product.'
          },
          {
            question: 'Can you shape the schema around our workflow?',
            answer: 'Yes. The point of the offer is to tailor field selection, market scope, and delivery format so the data fits the workflow instead of creating cleanup work for your team.'
          },
          {
            question: 'How fresh is the data?',
            answer: 'PolyLab currently works from hourly market snapshots. That is well suited for research, scouting, ranking, and monitoring workflows, but it is not sold as high-frequency execution infrastructure.'
          }
        ]
      }
    },
    faq: [
      {
        question: 'What is PolyLab?',
        answer: 'PolyLab is an independent market scanner and analysis layer for Polymarket. It helps traders move from raw market lists to faster discovery using filters, spread, APR, liquidity, and smart-money context.'
      },
      {
        question: 'Do I need a wallet to use it?',
        answer: 'No. You can open the scanner and explore markets without connecting a wallet.'
      },
      {
        question: 'Can I use PolyLab for free?',
        answer: 'Yes. PolyLab is currently free for all users during early access. There is no paid subscription yet, though paid plans may be introduced later as the product evolves.'
      },
      {
        question: 'What does Smart Money mean?',
        answer: 'In PolyLab, Smart Money refers to holder behavior enriched with profitable-versus-losing trader context. It is meant to highlight positioning patterns, not to guarantee that one side is right.'
      },
      {
        question: 'How is APR calculated?',
        answer: 'APR is an estimate based on the current outcome price and the time remaining until the market expires. It represents a modeled annualized return if current odds hold, not a guaranteed return.'
      },
      {
        question: 'Why is the data updated hourly?',
        answer: 'PolyLab currently works from hourly market snapshots. That cadence is designed to support signal-oriented research and market scouting without pretending to be second-by-second execution infrastructure.'
      },
      {
        question: 'Is PolyLab affiliated with Polymarket?',
        answer: 'No. PolyLab is an independent third-party tool and is not officially affiliated with, endorsed by, or partnered with Polymarket.'
      },
      {
        question: 'How can I contact you?',
        answer: 'You can reach us at hello@polylab.app for product questions, feedback, or partnership inquiries.'
      }
    ],
    terms: [
      'PolyLab is provided for informational and analytical purposes only. We do not provide financial, investment, or legal advice.',
      'The tool and all calculated metrics such as APR and spread are provided as-is without guarantees of accuracy. Always verify important information on the official Polymarket website.',
      'Prediction markets involve significant risk of capital loss. PolyLab is not responsible for financial decisions or losses incurred through use of the product.',
      'PolyLab is an independent tool and is not affiliated with, endorsed by, or partnered with Polymarket or Gamma.'
    ],
    privacy: [
      'Data Collection: We do not collect personal information from visitors browsing the public scanner. If you contact us by email, we only use your address to respond.',
      'Authentication: If you use Supabase Auth, we only store the minimum necessary account information required to manage your session and preferences.',
      'Cookies: We use essential cookies to manage authentication and product session behavior.',
      'Third Parties: We do not sell your data. Market data is sourced from public APIs and product infrastructure providers needed to operate PolyLab.'
    ]
  });
}());
