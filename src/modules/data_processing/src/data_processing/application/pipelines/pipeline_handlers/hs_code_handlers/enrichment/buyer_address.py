import pandas as pd

from data_processing.domain.models.processed_data import (
    ProcessedData,
)
from data_processing.domain.models.base_handler import BaseProcessingHandler


class BuyerAddressGroupingHandler(BaseProcessingHandler):
    """Group buyers by importer address and enrich dataframe with buyer_count."""

    def __init__(self) -> None:
        self.step_name = "group_buyer_by_address"

    def _process(self, data: ProcessedData) -> ProcessedData:

        # Step 2: Get dataframe from structured_data
        df = data.dataframe
        # Step 3: Delegate real processing to process_handler
        return self.process_handler(data=data, df=df)

    def process_handler(
        self,
        data: ProcessedData,
        df: pd.DataFrame,
    ) -> ProcessedData:
        try:
            # Step 4: Group buyer_name by importer_address_vn
            grouped_df = (
                df.groupby("importer_address_vn")["buyer_name"]
                .agg(
                    buyer_set=lambda series: set(
                        buyer for buyer in series.dropna() if str(buyer).strip()
                    ),
                    buyer_count=lambda series: series.nunique(),
                )
                .reset_index()
                .sort_values("buyer_count", ascending=False)
            )

            # Step 5: Enrich original dataframe with buyer_count
            enriched_df = df.merge(
                grouped_df[["importer_address_vn", "buyer_count"]],
                on="importer_address_vn",
                how="left",
            )

            # Step 6: Build processing result
            result = {
                "one_address_many_buyers": int(
                    (grouped_df["buyer_count"] > 1).sum()
                ),
                "grouped_rows": int(len(grouped_df)),
            }

            # Step 7: Update structured_data
            data.dataframe = enriched_df
            data.processing_steps = data.processing_steps+ [{self.step_name: {"status": "success", **result}}]
            # Step 8: Return success result
            return data

        except Exception as exc:
            # Step 9: Handle failed grouping process
            error = f"group buyer by address failed: {exc}"

            structured_data = dict(data.structured_data)
            processing_step = dict(structured_data.get("processing_step", {}))
            processing_step[self.step_name] = {
                "status": "failed",
                "error": error,
            }
            structured_data["processing_step"] = processing_step

            return data.model_copy(
                update={
                    "structured_data": structured_data,
                    "is_valid": False,
                    "processing_steps": data.processing_steps
                    + [{self.step_name: {"status": "failed", "error": error}}],
                }
            )
