import React from 'react';

interface ReviewCardProps {
    task_id: string;
    generated_content: string | null;
    confidence_score: number;
    reasoning_trace: string;
}

const ReviewCard: React.FC<ReviewCardProps> = ({ task_id, generated_content, confidence_score, reasoning_trace }) => {
    const getBadgeColor = (score: number) => {
        if (score > 0.9) return 'bg-green-100 text-green-800';
        if (score > 0.7) return 'bg-yellow-100 text-yellow-800';
        return 'bg-red-100 text-red-800';
    };

    const isLowConfidence = confidence_score < 0.8;

    const handleApprove = () => {
        console.log(`Approving task ${task_id}`);
        alert(`Approved Task ${task_id}`);
    };

    const handleReject = () => {
        console.log(`Rejecting task ${task_id}`);
        alert(`Rejected Task ${task_id}`);
    };

    return (
        <div className={`bg-white shadow rounded-lg p-6 mb-4 ${isLowConfidence ? 'border-2 border-red-500' : 'border border-gray-200'}`}>
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-lg font-medium text-gray-900">Task Review needed</h3>
                    <p className="text-sm text-gray-500">ID: {task_id}</p>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBadgeColor(confidence_score)}`}>
                    Confidence: {(confidence_score * 100).toFixed(0)}%
                </span>
            </div>

            <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Generated Content:</h4>
                <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 font-mono whitespace-pre-wrap">
                    {generated_content || "No text content generated."}
                </div>
            </div>

            <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Reasoning Trace:</h4>
                <p className="text-sm text-gray-600 italic border-l-2 border-gray-300 pl-3">
                    "{reasoning_trace}"
                </p>
            </div>

            <div className="flex justify-end space-x-3">
                <button
                    onClick={handleReject}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                    Reject
                </button>
                <button
                    onClick={handleApprove}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                    Approve
                </button>
            </div>

            {isLowConfidence && (
                <div className="mt-3 text-xs text-red-600 font-bold">
                    ⚠️ High Attention Needed: Confidence below safety threshold.
                </div>
            )}
        </div>
    );
};

export default ReviewCard;
