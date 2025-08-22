import express from 'express'
import {
  CopilotRuntime,
  copilotRuntimeNodeHttpEndpoint,
  EmptyAdapter,
} from "@copilotkit/runtime";

const app = express();

const serviceAdapter = new EmptyAdapter();

app.use('/api/copilotkit', (req, res, next) => {
    (async () => {
        const runtime = new CopilotRuntime({
            remoteEndpoints: [
                {
                    url: "http://localhost:8000/copilotkit",
                },
            ],
        });
        const handler = copilotRuntimeNodeHttpEndpoint({
            runtime,
            serviceAdapter,
            endpoint: "/api/copilotkit",
        });
        
        // Actually call the handler
        await handler(req, res);
    })().catch(next);
});

app.listen(4000, () => {
    console.log("Listening at http://localhost:4000/api/copilotkit");
});
