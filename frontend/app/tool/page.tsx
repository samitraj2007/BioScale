import type { Metadata } from "next";

import PhenotypicAgeTool from "@/components/PhenotypicAgeTool";

export const metadata: Metadata = {
  title: "Tool",
  description:
    "Estimate phenotypic age from health and lifestyle inputs using the BioScale lifestyle regression model.",
};

export default function ToolPage() {
  return (
    <div className="container-content py-12 sm:py-16">
      <header className="max-w-2xl">
        <p className="eyebrow">Interactive demo</p>
        <h1 className="mt-2 text-headline-md text-on-surface sm:text-display-md">
          Phenotypic Age Tool
        </h1>
        <p className="mt-4 text-body-lg text-on-surface-variant">
          Enter health and lifestyle characteristics to obtain a model-based
          estimate of phenotypic (biological) age. Inputs map to the feature set
          used to train the lifestyle regression model. For demonstration only —
          not medical advice.
        </p>
      </header>

      <div className="mt-10">
        <PhenotypicAgeTool />
      </div>
    </div>
  );
}
