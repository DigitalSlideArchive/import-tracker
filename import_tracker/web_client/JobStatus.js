import JobStatus from '@girder/jobs/JobStatus';

const jobPluginIsCancelable = JobStatus.isCancelable;
JobStatus.isCancelable = function (job) {
    if (job.get('type').startsWith('assetstore_import')) {
        return ![JobStatus.CANCELED, JobStatus.SUCCESS, JobStatus.ERROR].includes(job.get('status'));
    }
    return jobPluginIsCancelable(job);
};
