import DetailPage from "../../components/DetailPage";

export const metadata = {
  title: "Kp / Dst / SYM-H",
  description: "Storm indices for Earth impacts and satellite risk."
};

export default function Page() {
  return (
    <DetailPage
      title="Kp / Dst / SYM-H"
      meta="Storm indices for Earth impacts and satellite risk."
      cards={[
        {
          title: "Geospace Indices (1 day)",
          image: "https://services.swpc.noaa.gov/images/geospace/geospace_1_day.png",
          alt: "Geospace indices"
        },
        {
          title: "Planetary Kp",
          image: "https://services.swpc.noaa.gov/images/planetary-k-index.png",
          alt: "Planetary Kp index"
        }
      ]}
    />
  );
}
