import DetailPage from "../../components/DetailPage";

export const metadata = {
  title: "Radiation (Protons)",
  description: "Proton flux monitors satellite radiation risk."
};

export default function Page() {
  return (
    <DetailPage
      title="Radiation (Protons)"
      meta="Proton flux monitors satellite radiation risk."
      cards={[
        {
          title: "Proton Flux",
          image: "https://services.swpc.noaa.gov/images/ace-epam-7-day.gif",
          alt: "Proton flux"
        }
      ]}
    />
  );
}
