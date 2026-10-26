# Official JLC source observations

Observed 2026-10-22, approximately 15:19–15:24 UTC. Public service statements only; no exact-job approval, stock allocation, quote or account interaction. No full articles are quoted in the review. Help Center articles inspected label last update September 9, 2026.

| Local snapshot | Official URL | SHA256 |
| --- | --- | --- |
| pcb-capabilities.html | https://jlcpcb.com/capabilities/pcb-capabilities | fad333d76142917a1e692f96043e760f063bc551b9740b6f0f2710752a70e99b |
| pcba-capabilities.html | https://jlcpcb.com/capabilities/pcb-assembly-capabilities | 8b5136680d8dec5f450f28413fcdc6a56b44343f5aabd72928de4a39142a2b9e |
| assembly-faq.html | https://jlcpcb.com/help/article/pcb-assembly-faqs | 2d8b247695981f3890404623ea7325310f7ed179a565c66d520206e794b02a37 |
| assembly-terms.html | https://jlcpcb.com/help/article/terms-and-conditions-of-jlcpcb-assembly-service | 3c71cc2540c83d5b6b49de4ea40fbde20eef02ff40e98089f4b87f4db8330f98 |
| consignment-terms.html | https://jlcpcb.com/help/article/consignment-part-terms-conditions | 2cf4cbb57afa6fbeea161eb86d773706a54a96b521f1375454ec3a5a7cfdda89 |
| own-parts.html | https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order | 8282803623e746babd80cb4794551acb552a6c83c529c7faf8c69fb0cc3e1756 |
| personalized.html | https://jlcpcb.com/help/article/jlcpcb-supported-personalized-services | a7672e8a3c833e912a3ddee59c0b70187a8f7fa0a655cf7702583266e336a958 |
| programming.html | https://jlcpcb.com/help/article/pcba-programming-service | d98df4d1c1c1ab0e5e23476b4130928674106b8c316c1c215f6dc0e17ba26a7f |
| stencil-data.html | https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders | 341a5a164413bf6db5ea6e9a7712bf1d0873359e8e504a9b136a9a236a54ba13 |

Successfully read official browser-rendered pages, but one raw curl attempt each returned HTTP429; no raw HTML claimed retained:

- [Global sourcing guide](https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service): assembly-only service/warehousing, review, minimum quantities and non-kit scope.
- [Global sourcing terms](https://jlcpcb.com/help/article/global-sourcing-parts-order-terms-conditions): paid-order cancellation limitations, unsupported-line refund scope, received-stock requirement, inventory-pool restrictions and unassembled-parts shipment restriction.

Key local evidence remains the exact preserved first-run packet and original LS43/LS33 instructions; public capability limits do not rewrite them. Packet files and ZIP were rehashed during this review without modification. Actual source/demand arithmetic was previously independently reviewed in REVIEW.md and review-checks.json; it was not upgraded to a manufacturing receipt here.
