// Minimal inline-SVG icon set (Heroicons-outline style, hand-picked subset).
// Deliberately not pulling in an icon package - keeps the build dependency-free.
import type { SVGProps } from "react";

const base = (props: SVGProps<SVGSVGElement>) => ({
  xmlns: "http://www.w3.org/2000/svg",
  fill: "none",
  viewBox: "0 0 24 24",
  strokeWidth: 1.75,
  stroke: "currentColor",
  ...props,
});

export const SparklesIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z" />
  </svg>
);

export const CheckCircleIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m9 12.75 2.25 2.25L15 10.5m6 1.5a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

export const XCircleIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

export const ExclamationTriangleIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376C1.83 17.42 2.694 19 4.132 19h15.736c1.438 0 2.303-1.581 1.435-2.874L13.435 4.126c-.719-1.076-2.152-1.076-2.87 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
  </svg>
);

export const BellIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
  </svg>
);

export const ClipboardIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3a2.25 2.25 0 0 0-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" />
  </svg>
);

export const ShieldIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.623 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
  </svg>
);

export const ArrowTrendingUpIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 18 6.41-6.41a2.25 2.25 0 0 1 3.18 0l2.16 2.16a2.25 2.25 0 0 0 3.18 0L21.75 9M15 9h6.75V15.75" />
  </svg>
);

export const ListBulletIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM3.75 12h.007v.008H3.75V12Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm-.375 5.25h.007v.008H3.75v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
  </svg>
);

export const ClockIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

export const DocumentPlusIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m5.231 13.481L12 17.25l-1.481-1.481a2.25 2.25 0 0 1 0-3.182l.331-.331a2.25 2.25 0 0 1 3.182 0l.331.331a2.25 2.25 0 0 1 0 3.182l-.081.081ZM14.25 2.25c.966 0 1.75.784 1.75 1.75v.75c0 .966-.784 1.75-1.75 1.75h-.75a1.75 1.75 0 0 1-1.75-1.75V4c0-.966.784-1.75 1.75-1.75h.75Z" />
  </svg>
);

export const ChevronDownIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg {...base(props)}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
  </svg>
);
