// components/JsonBlock.tsx
export default function JsonBlock({ value }: { value: any }) {
  return (
    <pre className="text-sm overflow-auto whitespace-pre-wrap break-words bg-gray-50 rounded-xl p-4">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}
