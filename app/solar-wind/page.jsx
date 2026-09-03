import DetailPage from "../../components/DetailPage";

export const metadata = {
  title: "Solar Wind & IMF",
  description: "Real-time drivers for geomagnetic storms and satellite drag."
};

export default function Page() {
  return (
    <DetailPage
      title="Solar Wind & IMF"
      meta="Real-time drivers for geomagnetic storms and satellite drag."
      cards={[
        {
          title: "ACE MAG/SWEPAM (2-hour)",
          image: "https://services.swpc.noaa.gov/images/ace-mag-swepam-2-hour.gif",
          alt: "ACE solar wind"
        },
        {
          title: "Solar Wind Overview",
          image: "https://services.swpc.noaa.gov/experimental/images/swx-overview-large.gif",
          alt: "Space weather overview"
        }
      ]}
    />
  );
}
